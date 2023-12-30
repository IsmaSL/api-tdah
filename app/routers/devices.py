from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models
from ..schemas import DevicePublic
from ..dependencies import get_db, get_current_active_user

router = APIRouter()

@router.get("/get-devices", response_model=List[DevicePublic])
def get_devices(
        current_user: models.Usuario = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
    devices = db.query(models.Dispositivo).all()
    return devices