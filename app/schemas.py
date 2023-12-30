from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

# Resultado EEG
class EEGRequest(BaseModel):
    id_user: str
    filename: str

# Login
class UserLogin(BaseModel):
    correo: EmailStr
    contraseña: str

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    urlImg: Optional[str] = None
    nombre: str
    apellidoP: str
    apellidoM: Optional[str] = None
    rol: str
    correo: EmailStr
    contraseña: str

    class Config:
        from_attributes = True

class DatosGenerales(BaseModel):
    fechaNacimiento: Optional[date]
    sexo: Optional[str]
    ciudadResidencia: Optional[str]
    numTelefono: Optional[str]
    numTelefonoFam: Optional[str]
    ocupacion: Optional[str]

class DatosClinicos(BaseModel):
    adhd: Optional[int]
    add: Optional[int]
    bipolar: Optional[int]
    unipolar: Optional[int]
    anxiety: Optional[int]
    substance: Optional[int]
    med: Optional[int]

class UserPublic(BaseModel):
    idUsuario: int
    urlImg: Optional[str] = None
    nombre: str
    apellidoP: str
    apellidoM: Optional[str] = None
    rol: str
    correo: EmailStr
    fechaRegistro: date
    datos_generales: Optional[DatosGenerales]
    datos_clinicos: Optional[DatosClinicos]

    class Config:
        from_attributes = True

class UsuarioReport(BaseModel):
    idUsuario: int
    nombre: str
    apellidoP: str
    apellidoM: str
    datos_generales: DatosGenerales

    class Config:
        from_attributes = True

class UserPasswordUpdate(BaseModel):
    contraseña_actual: str
    contraseña_nueva: str

    class Config:
        from_attributes = True

class TokenData(BaseModel):
    correo: str = None

# Dispositivos
class DevicePublic(BaseModel):
    idTipoDispositivo: int
    url_img: Optional[str] = None
    nombre: str
    marca: str
    modelo: str
    tipo: str
    descripcion: str

    class Config:
        from_attributes = True

class DeviceName(BaseModel):
    nombre: str
    url_img: str

class DetallePrueba(BaseModel):
    idDetallePrueba: Optional[int] = None
    idEvaluacion: Optional[int] = None
    nivelAtencion: str
    nivelActividad: str
    observaciones: Optional[str] = None
    diagnosticoMedico: str
    justificacionMedico: Optional[str] = None
    urlCsv: str

    class Config:
        from_attributes = True

class Prueba(BaseModel):
    idPrueba: Optional[int] = None
    idPaciente: int
    idDetallePrueba: Optional[int] = None
    idTipoDispositivo: int
    fecha_prueba: date
    hora_prueba: str
    tiempo_prueba: str
    probabilidad: float
    diagnosticoFinal: str
    tipo_dispositivo: Optional[DeviceName] = None
    detalle_prueba: DetallePrueba
    usuario: Optional[UsuarioReport] = None

    class Config:
        from_attributes = True

class PruebaUpdate(BaseModel):
    idPrueba: int
    probabilidad: Optional[float] = None
    diagnosticoFinal: Optional[str] = None

class DetallePruebaUpdate(BaseModel):
    idDetallePrueba: int
    nivelAtencion: str

class DiagnosticoEntrada(BaseModel):
    nivelActividadFisica: str
    nivelAtencion: str
    diagnosticoMedico: str

class DiagnosticoSalida(BaseModel):
    diagnosticoFinal: int
    probabilidadPrevalencia: float
    
class DatosGeneralesCreatePatient(BaseModel):
    fechaNacimiento: Optional[date]
    sexo: Optional[str]
    ciudadResidencia: Optional[str]
    numTelefono: Optional[str]
    numTelefonoFam: Optional[str]
    ocupacion: Optional[str]

class UsuarioCreatePatient(BaseModel):
    urlImg: Optional[str]
    nombre: str
    apellidoP: str
    apellidoM: Optional[str]
    rol: str
    correo: str
    contraseña: Optional[str]
    fechaRegistro: date
    estado: str
    datos_generales: DatosGeneralesCreatePatient

class AddDetallePrueba(BaseModel):
    idEvaluacion: Optional[int] = None
    nivelAtencion: str
    nivelActividad: str
    observaciones: Optional[str]
    diagnosticoMedico: str
    justificacionMedico: Optional[str]
    urlCsv: str

    class Config:
        from_attributes = True

class AddPrueba(BaseModel):
    idPaciente: Optional[int] = None
    idDetallePrueba: Optional[int] = None
    idTipoDispositivo: Optional[int] = None
    fecha_prueba: date
    hora_prueba: str
    tiempo_prueba: str
    probabilidad: float
    diagnosticoFinal: str
    detalle_prueba: AddDetallePrueba

    class Config:
        from_attributes = True

class ScoreForm(BaseModel):
    idUsuario: int
    asrs: Optional[int] = None
    wurs: Optional[int] = None
    mdq: Optional[int] = None
    ct: Optional[int] = None
    madrs: Optional[int] = None
    hads_a: Optional[int] = None
    hads_d: Optional[int] = None

class ScoreFormUpdate(BaseModel):
    idPaciente: int
    form: str
    score: int