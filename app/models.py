# Definición de los modelos de SQLAlchemy.
from sqlalchemy import CHAR, DECIMAL, Column, ForeignKey, Integer, String, Date
from sqlalchemy.orm import relationship
from .database import Base

# Modelo SQLAlchemy para la tabla 'usuarios'
class Usuario(Base):
    __tablename__ = "usuarios"
    idUsuario = Column(Integer, primary_key=True, index=True)
    urlImg = Column(String(255))
    nombre = Column(String(100))
    apellidoP = Column(String(100))
    apellidoM = Column(String(100))
    rol = Column(String(100))
    correo = Column(String(100), unique=True, index=True)
    contraseña = Column(String(255))
    fechaRegistro = Column(Date)
    estado = Column(CHAR(1))

    datos_generales = relationship("DatosGenerales", back_populates="usuario", uselist=False)
    datos_clinicos = relationship("DatosClinicos", back_populates="usuario", uselist=False)
    pruebas = relationship("Prueba", back_populates="usuario")

class DatosGenerales(Base):
    __tablename__ = 'datos_generales'
    idUsuario = Column(Integer, ForeignKey('usuarios.idUsuario'), primary_key=True)
    fechaNacimiento = Column(Date)
    sexo = Column(CHAR(1))
    ciudadResidencia = Column(String)
    numTelefono = Column(String)
    numTelefonoFam = Column(String)
    ocupacion = Column(String)

    usuario = relationship("Usuario", back_populates="datos_generales")

class DatosClinicos(Base):
    __tablename__ = 'datos_clinicos'
    idUsuario = Column(Integer, ForeignKey('usuarios.idUsuario'), primary_key=True)
    adhd = Column(CHAR)
    add = Column(CHAR)
    bipolar = Column(CHAR)
    unipolar = Column(CHAR)
    anxiety = Column(CHAR)
    substance = Column(CHAR)
    med = Column(CHAR)

    usuario = relationship("Usuario", back_populates="datos_clinicos")

class Dispositivo(Base):
    __tablename__ = "tipos_dispositivos"
    idTipoDispositivo = Column(Integer, primary_key=True, index=True)
    url_img = Column(String(255))
    nombre = Column(String(25))
    marca = Column(String(100))
    modelo = Column(String(100))
    tipo = Column(String(100))
    descripcion = Column(String(255))

class DetallePrueba(Base):
    __tablename__ = 'detalle_pruebas'
    idDetallePrueba = Column(Integer, primary_key=True, autoincrement=True)
    idEvaluacion = Column(Integer)
    nivelAtencion = Column(String(25)) 
    nivelActividad = Column(String(25))
    observaciones = Column(String)
    diagnosticoMedico = Column(String(25))
    justificacionMedico = Column(String(255))
    urlCsv = Column(String(255))

    pruebas = relationship("Prueba", back_populates="detalle_prueba")

class Prueba(Base):
    __tablename__ = 'pruebas'
    idPrueba = Column(Integer, primary_key=True, autoincrement=True)
    idPaciente = Column(Integer, ForeignKey('usuarios.idUsuario'))
    idTipoDispositivo = Column(Integer, ForeignKey('tipos_dispositivos.idTipoDispositivo'))
    idDetallePrueba = Column(Integer, ForeignKey('detalle_pruebas.idDetallePrueba'))
    fecha_prueba = Column(Date)
    hora_prueba = Column(String(10))
    tiempo_prueba = Column(String(10))
    probabilidad = Column(DECIMAL(5,2))
    diagnosticoFinal = Column(String(25))

    usuario = relationship("Usuario", back_populates="pruebas")
    tipo_dispositivo = relationship("Dispositivo")
    detalle_prueba = relationship("DetallePrueba", back_populates="pruebas")

class ScoreForm(Base):
    __tablename__ = 'score_forms'
    idUsuario = Column(Integer, primary_key=True, autoincrement=True)
    asrs = Column(Integer)
    wurs = Column(Integer)
    mdq = Column(Integer)
    ct = Column(Integer)
    madrs = Column(Integer)
    hads_a = Column(Integer)
    hads_d = Column(Integer)

# Definir las relaciones con otras tablas si las hay
# Por ejemplo, si 'usuarios' está relacionado con otra tabla llamada 'posts':
# posts = relationship("Post", back_populates="usuario")