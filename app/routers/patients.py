# Router de los pacientes
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from app import crud
from .. import models
from ..schemas import UsuarioCreatePatient, UserPublic
from ..dependencies import get_db, get_current_active_user
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import desc

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

