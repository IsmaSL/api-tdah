# Funciones relacionadas con la seguridad (hash de contraseñas, verificación, token JWT).
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from app.models import Usuario
from datetime import timedelta, datetime
from .settings import SECRET_KEY, ALGORITHM

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, correo: str):
    return db.query(Usuario).filter(Usuario.correo == correo).first()

def authenticate_user(db, correo: str, contraseña: str):
    user = get_user(db, correo)
    if not user:
        return False
    if not verify_password(contraseña, user.contraseña):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt