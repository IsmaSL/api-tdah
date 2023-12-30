from fastapi import APIRouter, Depends, HTTPException
from .. import schemas, models, crud
from ..dependencies import get_db, get_current_active_user
from sqlalchemy.orm import Session

router = APIRouter()

@router.get('/get-score-forms/{paciente_id}', response_model=schemas.ScoreForm)
def get_score_forms(
        paciente_id: int,
        current_user: models.Usuario = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
    forms = db.query(models.ScoreForm).filter(models.ScoreForm.idUsuario == paciente_id).first()
    if not forms:
        raise HTTPException(status_code=404, detail="El paciente no cuenta con formularios aplicados.")
    return forms

@router.post('/update-score-form/')
def update_score_form_endpoint(
        score_form_data: schemas.ScoreFormUpdate,
        current_user: models.Usuario = Depends(get_current_active_user), 
        db: Session = Depends(get_db)
    ):
    score_form_record = crud.update_or_create_score_form(db=db, score_data=score_form_data)

    # Crear una respuesta que coincida con el esquema de respuesta
    response_data = {
        "idUsuario": score_form_record.idUsuario,
        "ASRS": score_form_record.asrs,
        "WURS": score_form_record.wurs,
        "MDQ": score_form_record.mdq,
        "CT": score_form_record.ct,
        "MADRS": score_form_record.madrs,
        "HADS_A": score_form_record.hads_a,
        "HADS_D": score_form_record.hads_d
    }

    return response_data