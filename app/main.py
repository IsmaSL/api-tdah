from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from .routers import auth, users, devices, test, patients, forms, ml_ia
from .database import engine, Base
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()

Base.metadata.create_all(bind=engine)

# Configura CORS
origins = [
    "http://localhost:4200",  
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

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(devices.router, prefix="/devices", tags=["devices"])
app.include_router(test.router, prefix="/tests", tags=["tests"])
app.include_router(patients.router, prefix="/patients", tags=["patients"])
app.include_router(forms.router, prefix="/forms", tags=["forms"])
app.include_router(ml_ia.router, prefix="/machine", tags=["machine"])

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

@app.exception_handler(HTTPException)
async def unicorn_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )