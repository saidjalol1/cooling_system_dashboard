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

active_connections: list[WebSocket] = []

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



@device.websocket("/ws/motors")
async def websocket_motors(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await asyncio.sleep(2)
            with Session(database.engine) as db:
                motors = db.query(models.Device).all()

                data = []
                for d in motors:
                    last_temp = d.temperature[-1] if d.temperature else None
                    last_vibration = d.vibration[-1] if d.vibration else None
                    last_humidity = d.humidity[-1] if d.humidity else None

                    
                    temp_value = last_temp.heat if last_temp else None
                    vibration_value = last_vibration.vibration if last_vibration else None
                    humidity_value = last_humidity.humidity if last_humidity else None

                   
                    temp_time = last_temp.date_created.strftime("%M:%S") + " ago" if last_temp else "N/A"
                    vibration_time = last_vibration.date_created.strftime("%M:%S") + " ago" if last_vibration else "N/A"
                    humidity_time = last_humidity.date_created.strftime("%M:%S") + " ago" if last_humidity else "N/A"

                    data.append({
                        "id": d.id,
                        "name": d.device_name,
                        "zone": d.device_zone,
                        "temp_value": temp_value,
                        "vibration_value": vibration_value,
                        "humidity_value": humidity_value,
                        "temp_time": temp_time,
                        "vibration_time": vibration_time,
                        "humidity_time": humidity_time,
                    })
                    print(data)
            
            for conn in list(active_connections):
                try:
                    await conn.send_text(json.dumps(data))
                except Exception:
                    
                    active_connections.remove(conn)
    except WebSocketDisconnect:
        active_connections.remove(websocket)