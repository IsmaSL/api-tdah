# Dependencias que pueden ser reutilizadas en diferentes rutas/endpoints.
# Configuración de la base de datos y sesión SQLAlchemy.
from .database import SessionLocal, Base
# Resto de bibliotecas
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from .settings import SECRET_KEY, ALGORITHM
from . import schemas, models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_active_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Las credenciales no existen o no son válidas.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        correo: str = payload.get("sub")
        if correo is None:
            raise credentials_exception
        token_data = schemas.TokenData(correo=correo)
    except JWTError:
        raise credentials_exception
    user = db.query(models.Usuario).filter(models.Usuario.correo == token_data.correo).first()
    if user is None:
        raise credentials_exception
    return user