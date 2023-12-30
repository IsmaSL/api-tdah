# Router de los usuarios
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from .. import models
from app.security import get_password_hash
from ..schemas import UserCreate, UserPublic
from ..dependencies import get_db, get_current_active_user
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/create-user", response_model=UserPublic)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Verificar si el correo ya existe
    db_user = db.query(models.Usuario).filter(models.Usuario.correo == user.correo).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Correo ya registrado.")

    hashed_password = get_password_hash(user.contraseña)

    db_user = models.Usuario(
        correo=user.correo,
        contraseña=hashed_password,
        nombre=user.nombre,
        apellidoP=user.apellidoP,
        apellidoM=user.apellidoM,
        rol=user.rol,
        fechaRegistro=datetime.utcnow(),
        urlImg=user.urlImg
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

@router.get("/count-patients/")
def count_users_patients(
        current_user: models.Usuario = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
    patient_count = db.query(models.Usuario).filter(models.Usuario.rol == "Paciente").count()

    return { "count_patients": patient_count }