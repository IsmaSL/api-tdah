# Router de los pacientes
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from app import crud
from .. import models
from ..schemas import PrediccionEntrada, PromedioRespuesta, UsuarioCreatePatient, UserPublic, UserRecent
from ..dependencies import get_db, get_current_active_user
from sqlalchemy.orm import Session
from typing import List

router = APIRouter()

@router.post("/add-patient/", response_model=UsuarioCreatePatient)
def add_patient(
        usuario: UsuarioCreatePatient, 
        current_user: models.Usuario = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
    return crud.create_patient(db=db, usuario=usuario)

@router.get("/get-patients", response_model=List[UserPublic])
def get_patients(
        current_user: models.Usuario = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
    pacientes = db.query(models.Usuario).filter(models.Usuario.rol == "Paciente").order_by(models.Usuario.nombre).all()
    return pacientes

@router.get("/get-recente-patients", response_model=list[UserRecent])
def get_recent_patients(
        db: Session = Depends(get_db)
    ):
    try:
        ultimos_pacientes = crud.get_recent_patients(db)
        return ultimos_pacientes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/get-patient-info/{paciente_id}", response_model=UserPublic)
def get_paciente(
        paciente_id: int,
        current_user: models.Usuario = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
    # Verificar si el usuario actual tiene permiso para ver la información
    if current_user.rol != "Médico":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para acceder a esta información."
        )

    paciente = db.query(models.Usuario).filter(models.Usuario.idUsuario == paciente_id, models.Usuario.rol == "Paciente").first()

    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    # Cargar también los datos generales relacionados
    paciente_datos_generales = db.query(models.DatosGenerales).filter(models.DatosGenerales.idUsuario == paciente_id).first()
    paciente_datos_clinicos = db.query(models.DatosClinicos).filter(models.DatosClinicos.idUsuario == paciente_id).first()
    paciente.datos_generales = paciente_datos_generales
    paciente.datos_clinicos = paciente_datos_clinicos

    return paciente

@router.post("/final_results/", response_model=PromedioRespuesta)
def calcular_promedio_pruebas(
        datos: PrediccionEntrada, 
        current_user: models.Usuario = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
    resultado = crud.calcular_promedio_pruebas(db, datos.idPaciente, datos.prediccionML)

    if resultado is None:
        raise HTTPException(status_code=404, detail="No se encontraron pruebas para el paciente.")
    
    # Buscar o crear un registro en datos_clinicos
    datos_clinicos = db.query(models.DatosClinicos).filter(models.DatosClinicos.idUsuario == datos.idPaciente).first()
    if not datos_clinicos:
        # Crear nuevo registro si no existe
        datos_clinicos = models.DatosClinicos(idUsuario=datos.idPaciente)
        db.add(datos_clinicos)
    
    # Actualizar datos
    datos_clinicos.adhd = str(resultado['diagnostico']) if resultado['diagnostico'] is not None else None
    datos_clinicos.prob = resultado['prevalencia']
    datos_clinicos.fecha_diagnostico = date.today()

    db.commit()

    return resultado