# Router para la autenticación.
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from ..dependencies import get_db, get_current_active_user
from ..security import authenticate_user, create_access_token
from ..settings import ACCESS_TOKEN_EXPIRE_MINUTES
from ..schemas import UserPublic

router = APIRouter()

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Autentica el usuario
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verifica si el rol del usuario es 'Médico'
    if user.rol != "Médico":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No tienes permiso para iniciar sesión.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crea el token de acceso
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.correo}, expires_delta=access_token_expires
    )   
    return  { 
                "access_token": access_token, 
                "token_type": "bearer" 
            }

@router.get("/get-current-user", response_model=UserPublic)
async def get_current_user(
    current_user: UserPublic = Depends(get_current_active_user)
    ):
    return current_user