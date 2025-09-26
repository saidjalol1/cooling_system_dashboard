from typing import List
from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from config import database
from shemas import models, schemas



device = APIRouter(
    tags=["Devices"]
)


@device.post("/device/create", response_model=schemas.Device)
async def create_user(device: schemas.DeviceBase, db: Session = Depends(database.get_db)):
    device = models.Device(**device.model_dump())

    db.add(device)
    db.commit()
    db.refresh(device)

    return device


@device.post("/device/heat/create", response_model=schemas.Heat)
async def create_user(device: schemas.HeatBase, db: Session = Depends(database.get_db)):
    temp = models.Heat(**device.model_dump())

    db.add(temp)
    db.commit()
    db.refresh(temp)

    return temp


@device.post("/device/vibration/create", response_model=schemas.Vibration)
async def create_user(device: schemas.VibrationBase, db: Session = Depends(database.get_db)):
    temp = models.Vibration(**device.model_dump())

    db.add(temp)
    db.commit()
    db.refresh(temp)

    return temp


@device.get("/devices", response_model=List[schemas.Device])
async def create_user(db: Session = Depends(database.get_db)):
    devices = db.query(models.Device).all()
    return devices