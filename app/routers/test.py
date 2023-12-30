import os
import pandas as pd
import numpy as np
import tempfile

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import crud
from ..dependencies import get_db, get_current_active_user
from .. import schemas, models
from ..firebase.conn import storage
from ..schemas import DetallePruebaUpdate, DiagnosticoSalida, EEGRequest, Prueba, PruebaUpdate, DiagnosticoEntrada, AddPrueba
from scipy.signal import welch, butter, filtfilt

router = APIRouter()

@router.post("/process-eeg/")
async def process_eeg(request: EEGRequest):
    try:
        # Construir la ruta en Firebase Storage
        firebase_storage_path = "storage/files/test/user_" + request.id_user + "/" + request.filename
        # Crear un archivo temporal
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        bucket = storage.bucket()
        blob = bucket.blob(firebase_storage_path)
        blob.download_to_filename(temp_file.name)
        # Procesar el archivo
        df = pd.read_csv(temp_file.name)

        # Función para filtrar y eliminar el ruido
        def bandpass_filter(data, lowcut=0.5, highcut=50.0, fs=256, order=5):
            nyq = 0.5 * fs
            low = lowcut / nyq
            high = highcut / nyq
            b, a = butter(order, [low, high], btype='band')
            return filtfilt(b, a, data)

        # Función para obtener el poder medio en una banda de frecuencia específica
        def average_power(psd, freqs, start, end):
            return psd[(freqs >= start) & (freqs <= end)].mean()
        
        # Función para calcular el poder medio en ventanas de tiempo con mejor resolución en Welch
        def sliding_window_analysis(data, fs=256, nperseg=256*4):
            window_length = fs * 60  # 1 minuto
            num_windows = len(data) // window_length
            theta_avgs, beta_avgs, beta_theta_ratios = [], [], []

            for i in range(num_windows):
                segment = data[i*window_length:(i+1)*window_length]
                freqs, psd = welch(segment, fs, nperseg=nperseg)
                
                theta_power = average_power(psd, freqs, *theta)
                beta_power = average_power(psd, freqs, *beta)
                theta_avgs.append(theta_power)
                beta_avgs.append(beta_power)
                beta_theta_ratios.append(beta_power / theta_power if theta_power != 0 else 0)  # Evitar división por cero

            return theta_avgs, beta_avgs, beta_theta_ratios

        # Filtrado de los datos
        filtered_af7 = bandpass_filter(df['AF7'].to_numpy())
        filtered_af8 = bandpass_filter(df['AF8'].to_numpy())

        theta = (4, 8)
        beta = (13, 30)

        # Obtener el análisis de ventanas deslizantes para el canal AF7
        theta_avgs_af7, beta_avgs_af7, ratios_af7 = sliding_window_analysis(filtered_af7)
        theta_avgs_af8, beta_avgs_af8, ratios_af8 = sliding_window_analysis(filtered_af8)

        # Calcular el estado general de atención
        if np.mean(beta_avgs_af7) > np.mean(theta_avgs_af7):
            attention_state_AF7 = "Atento"
        elif np.mean(theta_avgs_af7) > np.mean(beta_avgs_af7):
            attention_state_AF7 = "Inatento"
        else:
            attention_state_AF7 = "Medianamente Atento"


        if np.mean(beta_avgs_af8) > np.mean(theta_avgs_af8):
            attention_state_AF8 = "Atento"
        elif np.mean(theta_avgs_af8) > np.mean(beta_avgs_af8):
            attention_state_AF8 = "Inatento"
        else:
            attention_state_AF8 = "Medianamente Atento"


        # Calcular el promedio de los cocientes para cada canal
        avg_ratio_af7 = sum(ratios_af7) / len(ratios_af7)
        avg_ratio_af8 = sum(ratios_af8) / len(ratios_af8)

        # Calcular el promedio general para ambos canales
        average_ratio = (avg_ratio_af7 + avg_ratio_af8) / 2

        if average_ratio > 1.2:
            final_state = "Atento"
        elif average_ratio < 0.8:
            final_state = "Inatento"
        else:
            final_state = "Medianamente Atento"


        return {
            "attention_state_AF7": attention_state_AF7,
            "attention_state_AF8": attention_state_AF8,
            # "avg_theta_af7": theta_avgs_af7,
            # "avg_beta_af7": beta_avgs_af7,
            # "avg_theta_af8": theta_avgs_af8,
            # "avg_beta_af8": beta_avgs_af8,
            "beta_theta_ratio_af7": ratios_af7,
            "beta_theta_ratio_af8": ratios_af8,
            "final_state": final_state
        }  
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        # Cerrar y eliminar el archivo temporal
        temp_file.close()
        os.remove(temp_file.name)

@router.get("/get-tests/{paciente_id}", response_model=List[Prueba]) 
def get_pruebas_by_paciente(
        paciente_id: int,
        db: Session = Depends(get_db),
        current_user: models.Usuario = Depends(get_current_active_user),
    ):

    pruebas = db.query(models.Prueba).filter(models.Prueba.idPaciente == paciente_id).all()
    if not pruebas:
        raise HTTPException(status_code=404, detail="No se encontraron pruebas para el paciente especificado")
    return pruebas

@router.get("/get-report/{id_prueba}", response_model=Prueba)
def get_prueba(
        id_prueba: int,
        db: Session = Depends(get_db),
        current_user: models.Usuario = Depends(get_current_active_user)
    ):
    prueba = db.query(models.Prueba).filter(models.Prueba.idPrueba == id_prueba).first()
    if not prueba:
        raise HTTPException(status_code=404, detail="Prueba no encontrada")
    return prueba

@router.put("/update-test-report", response_model=PruebaUpdate)
def update_prueba_prev_diag_final(
        prueba_update: schemas.PruebaUpdate,
        db: Session = Depends(get_db)
    ):
    # Buscar la prueba por su ID
    prueba = db.query(models.Prueba).filter(models.Prueba.idPrueba == prueba_update.idPrueba).first()
    if not prueba:
        raise HTTPException(status_code=404, detail="Prueba no encontrada")

    # Actualizar los campos necesarios
    if prueba_update.probabilidad is not None:
        prueba.probabilidad = prueba_update.probabilidad
    if prueba_update.diagnosticoFinal is not None:
        prueba.diagnosticoFinal = prueba_update.diagnosticoFinal
    # Guardar los cambios en la base de datos
    db.add(prueba)
    db.commit()
    db.refresh(prueba)
    return prueba

@router.put("/updated-test-detail-report", response_model=DetallePruebaUpdate)
def update_detalle_prueba_report(
        detalle_prueba_update: schemas.DetallePruebaUpdate,
        current_user: models.Usuario = Depends(get_current_active_user), 
        db: Session = Depends(get_db)
    ):
    # Buscar el detalle de prueba por su ID
    detalle_prueba = db.query(models.DetallePrueba).filter(models.DetallePrueba.idDetallePrueba == detalle_prueba_update.idDetallePrueba).first()
    if not detalle_prueba:
        raise HTTPException(status_code=404, detail="Detalle_Prueba no encontrada")
    # Actualizar los campos necesarios
    if detalle_prueba_update.nivelAtencion is not None:
        detalle_prueba.nivelAtencion = detalle_prueba_update.nivelAtencion
    # Guardar los cambios en la base de datos
    db.add(detalle_prueba)
    db.commit()
    db.refresh(detalle_prueba)
    return detalle_prueba

@router.post("/calcular-diagnostico/", response_model=DiagnosticoSalida)
def calcular_diagnostico_endpoint(
        data: DiagnosticoEntrada, 
        current_user: models.Usuario = Depends(get_current_active_user)
    ):
    resultado = crud.calcular_diagnostico_y_probabilidad(data)
    return resultado

@router.post("/save-test/", response_model=AddPrueba)
def save_test(
        prueba: AddPrueba, 
        current_user: models.Usuario = Depends(get_current_active_user), 
        db: Session = Depends(get_db)
    ):
    print(prueba)
    return crud.create_test(db=db, prueba=prueba)