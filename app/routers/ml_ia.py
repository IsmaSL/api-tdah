from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import joblib
import os

# # Obtener la ruta del directorio actual
current_dir = os.path.dirname(__file__)

# # Construir la ruta para el modelo y el escalador
model_path = os.path.join(current_dir, 'model', 'modelo_tdah.pkl')
scaler_path = os.path.join(current_dir, 'model', 'escalador_tdah.pkl')

# # Cargar el modelo y el escalador
model = joblib.load(model_path)
scaler = joblib.load(scaler_path)

# Cargar el modelo y el escalador
# model = joblib.load('./model/modelo_tdah.pkl')
# scaler = joblib.load('./model/escalador_tdah.pkl')

router = APIRouter()

class InputData(BaseModel):
    SEX: int
    AGE: int
    ADD: int
    BIPOLAR: int
    UNIPOLAR: int
    ANXIETY: int
    SUBSTANCE: int
    CT: int
    MDQ_POS: int
    WURS: int
    ASRS: int
    MADRS: int
    HADS_A: int
    HADS_D: int
    MED: int

@router.post("/predict")
def predict(data: InputData):
    try:
        # Convertir datos de entrada en un array de NumPy
        input_data = np.array([[data.SEX, data.AGE, data.ADD, data.BIPOLAR, data.UNIPOLAR,
                                data.ANXIETY, data.SUBSTANCE, data.CT, data.MDQ_POS, data.WURS,
                                data.ASRS, data.MADRS, data.HADS_A, data.HADS_D, data.MED]])
        # Escalar los datos
        input_data_scaled = scaler.transform(input_data)
        # Hacer la predicción
        prediction = model.predict(input_data_scaled)
        return {"prediction": int(prediction[0])}
    except:
        raise HTTPException(status_code=500, detail="Error en la predicción")