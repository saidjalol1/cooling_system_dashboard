import json
import asyncio
from typing import List
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect

from sqlalchemy.orm import Session

from config import database
from shemas import models, schemas



device = APIRouter(
    tags=["Devices"]
)



@device.post("/device/create")
async def create_user(device: schemas.DeviceBase, db: Session = Depends(database.get_db)):
    existing = db.query(models.Device).filter(
        models.Device.device_name == device.device_name
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Device already exists")

    new_device = models.Device(**device.model_dump())
    db.add(new_device)
    db.commit()
    db.refresh(new_device)
    return {"message":"created succfully", "device":new_device.device_name}


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


@device.post("/device/humidity/create", response_model=schemas.Humidity)
async def create_user(device: schemas.HumidityBase, db: Session = Depends(database.get_db)):
    temp = models.Humidity(**device.model_dump())

    db.add(temp)
    db.commit()
    db.refresh(temp)

    return temp


@device.get("/devices", response_model=List[schemas.Device])
async def create_user(db: Session = Depends(database.get_db)):
    devices = db.query(models.Device).all()
    return devices



