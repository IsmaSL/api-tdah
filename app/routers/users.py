# Router de los usuarios
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from app.security import get_password_hash
from .. import models, crud
from ..schemas import UserCreate, UserPublic, ConteoDiagnostico
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

@router.get("/count-patients")
def count_users_patients(
        current_user: models.Usuario = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
    patient_count = db.query(models.Usuario).filter(models.Usuario.rol == "Paciente").count()

    return { "count_patients": patient_count }

@router.get('/count-patients-adhd')
def count_patients_adhd(
        current_user: models.Usuario = Depends(get_current_active_user),
        db: Session = Depends(get_db)    
    ):
    patients_count = db.query(models.DatosClinicos).filter(
                            or_(
                                models.DatosClinicos.adhd == '1',
                                models.DatosClinicos.adhd == '2',
                                models.DatosClinicos.adhd == '3'
                            )
                        ).count()
    return { "count": patients_count }

@router.get('/history/{year}/{month}', response_model=ConteoDiagnostico)
def get_history(
        year: int, 
        month: int, 
        current_user: models.Usuario = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
    try:
        conteo = crud.get_conteo_diagnostico_mes(db, year, month)
        # Mapear las claves del diccionario a los nombres esperados por Pydantic
        conteo_diagnostico = ConteoDiagnostico(
            Sin_TDAH=conteo.get('0', 0),
            TDAH_Inatento=conteo.get('1', 0),
            TDAH_Hiperactivo=conteo.get('2', 0),
            TDAH_Mixto=conteo.get('3', 0)
        )
        return conteo_diagnostico
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))