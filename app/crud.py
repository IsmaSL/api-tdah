# Operaciones de la base de datos (Create, Read, Update, Delete).
from sqlalchemy import func, case
from sqlalchemy.orm import Session
from .models import DatosClinicos, DetallePrueba, Usuario, Prueba, DatosGenerales, ScoreForm
from .schemas import DiagnosticoEntrada, DiagnosticoSalida, UserCreate, PruebaUpdate, UsuarioCreatePatient, AddPrueba, ScoreFormUpdate, UserRecent
from .security import get_password_hash


def get_user_by_email(db: Session, email: str):
    return db.query(Usuario).filter(Usuario.correo == email).first()

def create_user(db: Session, user: UserCreate):
    fake_hashed_password = get_password_hash(user.contraseña)
    db_user = Usuario(**user.dict(), contraseña=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_pacientes(db: Session):
    return db.query(Usuario).filter(Usuario.rol == "Paciente").all()

def get_recent_patients(db: Session):
    ultimos_pacientes = db.query(Usuario).filter(
        Usuario.rol == 'Paciente',
        Usuario.estado == "1"
    ).order_by(
        Usuario.fechaRegistro.desc()
    ).limit(3).all()
    return [UserRecent.from_orm(paciente) for paciente in ultimos_pacientes]

def update_prueba(db: Session, update_data: PruebaUpdate):
    # Obtener el ID de la prueba del objeto update_data
    prueba_id = update_data.idPrueba

    # Buscar la prueba por su ID
    prueba = db.query(Prueba).filter(Prueba.idPrueba == prueba_id).first()
    if not prueba:
        return None  # O maneja esto de otra manera, como lanzar una excepción

    # Actualizar los campos necesarios
    if update_data.probabilidad is not None:
        prueba.probabilidad = update_data.probabilidad
    if update_data.diagnosticoFinal is not None:
        prueba.diagnosticoFinal = update_data.diagnosticoFinal

    # Guardar los cambios en la base de datos
    db.add(prueba)
    db.commit()
    db.refresh(prueba)
    return prueba

def calcular_probabilidad(coincidencias: int) -> float:
    if coincidencias == 3:
        return 0.90  # 90% de probabilidad
    elif coincidencias == 2:
        return 0.75  # 75% de probabilidad
    else:
        return 0.40  # 40% o menos de probabilidad

def calcular_diagnostico_y_probabilidad(data: DiagnosticoEntrada) -> DiagnosticoSalida:
    nivel_actividad_fisica = int(data.nivelActividadFisica)
    nivel_atencion = int(data.nivelAtencion)
    diagnostico_medico = int(data.diagnosticoMedico)

    # Aplicar las reglas para determinar el diagnóstico
    diagnostico = None
    if (nivel_actividad_fisica, nivel_atencion, diagnostico_medico) in [(3, 1, 0), (3, 2, 0)]:
        diagnostico = 0  # Sin TDAH
    elif (nivel_actividad_fisica, nivel_atencion, diagnostico_medico) in [(3, 3, 1), (2, 3, 1), (2, 2, 1)]:
        diagnostico = 1  # TDAH Inatento
    elif (nivel_actividad_fisica, nivel_atencion, diagnostico_medico) in [(1, 3, 2), (1, 2, 2), (2, 2, 2)]:
        diagnostico = 2  # TDAH Hiperactivo
    elif (nivel_actividad_fisica, nivel_atencion, diagnostico_medico) in [(1, 3, 3), (1, 2, 3), (2, 3, 3)]:
        diagnostico = 3  # TDAH Mixto

    # Calcular coincidencias para determinar la probabilidad
    coincidencias = 0
    if nivel_atencion == 3 and nivel_actividad_fisica in [2, 3]:
        print('inatento + [a_moderada_baja]')
        coincidencias += 1
    if nivel_actividad_fisica == [1, 2] and diagnostico_medico == 2:
        print('a_alta + t-h')
        coincidencias += 1
    if nivel_actividad_fisica == 1 and nivel_atencion == 3 and diagnostico_medico == 3:
        print('a_alta + inatento + t-m')
        coincidencias += 1
    if diagnostico_medico == diagnostico:
        print('dm == ds')
        coincidencias += 1

    probabilidad = calcular_probabilidad(coincidencias)

    return DiagnosticoSalida(diagnosticoFinal=diagnostico, probabilidadPrevalencia=probabilidad)
    
def create_patient(db: Session, usuario: UsuarioCreatePatient):
    db_usuario = Usuario(**usuario.dict(exclude={"datos_generales", "datos_clinicos"}))
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)

    if usuario.datos_generales:
        usuario_datos_generales = DatosGenerales(
            idUsuario=db_usuario.idUsuario, **usuario.datos_generales.dict()
        )
        db.add(usuario_datos_generales)
        db.commit()
        db.refresh(usuario_datos_generales)

    if usuario.datos_clinicos:
        usuario_datos_clinicos = DatosClinicos(
            idUsuario=db_usuario.idUsuario, **usuario.datos_clinicos.dict()
        )
        db.add(usuario_datos_clinicos)
        db.commit()
        db.refresh(usuario_datos_clinicos)
    
    return db_usuario

def create_test(db: Session, prueba: AddPrueba):
    # Crear y guardar el detalle de la prueba
    detalle_prueba_data = prueba.detalle_prueba.dict()
    db_detalle_prueba = DetallePrueba(**detalle_prueba_data)
    db.add(db_detalle_prueba)
    db.commit()
    db.refresh(db_detalle_prueba)

    # Crear y guardar la prueba, incluyendo el id del detalle
    prueba_data = prueba.dict(exclude={"detalle_prueba", "idDetallePrueba"})
    prueba_data["idDetallePrueba"] = db_detalle_prueba.idDetallePrueba
    db_prueba = Prueba(**prueba_data)
    db.add(db_prueba)
    db.commit()
    db.refresh(db_prueba)

    return db_prueba

def update_or_create_score_form(db: Session, score_data: ScoreFormUpdate):
    score_record = db.query(ScoreForm).filter(ScoreForm.idUsuario == score_data.idPaciente).first()

    if score_record:
        # Mapea el nombre del formulario a la columna correspondiente y actualiza el valor
        if score_data.form == 'asrs':
            score_record.asrs = score_data.score
        elif score_data.form == 'wurs':
            score_record.wurs = score_data.score
        elif score_data.form == 'mdq':
            score_record.mdq = score_data.score
        elif score_data.form == 'ct':
            score_record.ct = score_data.score
        elif score_data.form == 'madrs':
            score_record.madrs = score_data.score
        elif score_data.form == 'hads_a':
            score_record.hads_a = score_data.score
        elif score_data.form == 'hads_d':
            score_record.hads_d = score_data.score

        db.add(score_record)
    else:
        # Crear un nuevo registro si no existe
        new_score_data = {"idUsuario": score_data.idPaciente, score_data.form: score_data.score}
        new_score_record = ScoreForm(**new_score_data)
        db.add(new_score_record)
    
    db.commit()
    return new_score_record if not score_record else score_record

def calcular_promedio_pruebas(db: Session, id_paciente: int, prediccion_ml: int):
    pruebas = db.query(Prueba).filter(Prueba.idPaciente == id_paciente).all()
    
    total_probabilidad = 0
    conteo_probabilidad = 0
    total_diagnostico = 0 if prediccion_ml == 0 else prediccion_ml * len(pruebas)  # Ajuste inicial basado en ML
    conteo_diagnostico = 0

    for prueba in pruebas:
        if prueba.probabilidad is not None:
            total_probabilidad += prueba.probabilidad
            conteo_probabilidad += 1
        if prueba.diagnosticoFinal is not None:
            total_diagnostico += int(prueba.diagnosticoFinal)
            conteo_diagnostico += 1

    promedio_probabilidad = total_probabilidad / conteo_probabilidad if conteo_probabilidad > 0 else None
    promedio_diagnostico = total_diagnostico / conteo_diagnostico if conteo_diagnostico > 0 else None

    # Ajustar el promedio a una categoría
    if promedio_diagnostico is not None:
        if promedio_diagnostico < 1.5:
            promedio_diagnostico = 0  # No tiene TDAH
        elif promedio_diagnostico < 2.5:
            promedio_diagnostico = 1  # TDAH Inatento
        elif promedio_diagnostico < 3.5:
            promedio_diagnostico = 2  # TDAH Hiperactivo
        else:
            promedio_diagnostico = 3  # TDAH Mixto

    return {"prevalencia": promedio_probabilidad, "diagnostico": promedio_diagnostico}

def get_conteo_diagnostico_mes(db: Session, year: int, month: int):
    conteo = {
        '0': 0,  # Sin_TDAH
        '1': 0,  # TDAH_Inatento
        '2': 0,  # TDAH_Hiperactivo
        '3': 0,  # TDAH_Mixto
    }

    resultados = db.query(
        DatosClinicos.adhd,
        func.count(DatosClinicos.idUsuario).label('conteo')
    ).filter(
        func.year(DatosClinicos.fecha_diagnostico) == year,
        func.month(DatosClinicos.fecha_diagnostico) == month,
        DatosClinicos.adhd.isnot(None)  # Asegurar que el diagnóstico no sea nulo
    ).group_by(
        DatosClinicos.adhd
    ).all()

    for resultado in resultados:
        conteo[resultado.adhd] = resultado.conteo

    return conteo