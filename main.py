from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

import pandas as pd
import numpy as np
from scipy.signal import welch, butter, filtfilt
from fastapi.middleware.cors import CORSMiddleware

# Configuraciones de la base de datos
DATABASE_URL = "mysql+pymysql://root:holamundo.1@localhost/tdah_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Instancia de FastAPI
app = FastAPI()

# Configura CORS
origins = [
    "http://localhost:4200",
    "http://localhost:58159"
    # La aplicación Angular se ejecuta en localhost:4200
    # Agregar aquí cualquier otro origen si es necesario
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return { "message": "Servidor en línea" } 


@app.post("/process-eeg/")
async def process_eeg(file: UploadFile = File(...)):
    if file and file.filename.endswith('.csv'):
        try:
            
            # Lee el archivo CSV y conviértelo en un DataFrame de Pandas
            df = pd.read_csv(file.file)

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
                attention_state_AF7 = "Distracción"
            else:
                attention_state_AF7 = "Medianamente atento"


            if np.mean(beta_avgs_af8) > np.mean(theta_avgs_af8):
                attention_state_AF8 = "Atento"
            elif np.mean(theta_avgs_af8) > np.mean(beta_avgs_af8):
                attention_state_AF8 = "Distracción"
            else:
                attention_state_AF8 = "Medianamente atento"


            # Calcular el promedio de los cocientes para cada canal
            avg_ratio_af7 = sum(ratios_af7) / len(ratios_af7)
            avg_ratio_af8 = sum(ratios_af8) / len(ratios_af8)

            # Calcular el promedio general para ambos canales
            average_ratio = (avg_ratio_af7 + avg_ratio_af8) / 2

            if average_ratio > 1.2:
                final_state = "Atento"
            elif average_ratio < 0.8:
                final_state = "Distracción"
            else:
                final_state = "Medianamente atento"


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
    else:
        raise HTTPException(status_code=400, detail="Invalid file format!")
