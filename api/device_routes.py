import json
import asyncio
from typing import List
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query

from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

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
    # Optimized query with eager loading to reduce database hits
    devices = db.query(models.Device).all()
    return devices


@device.get("/device/{device_id}/data")
async def get_device_data_by_date(
    device_id: int,
    start_date: date = Query(None),
    end_date: date = Query(None),
    db: Session = Depends(database.get_db)
):
    """
    Get device data filtered by date range
    If no dates provided, returns all data
    """
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Build date filters
    filters = []
    if start_date:
        filters.append(models.Heat.date_created >= datetime.combine(start_date, datetime.min.time()))
        filters.append(models.Vibration.date_created >= datetime.combine(start_date, datetime.min.time()))
        filters.append(models.Humidity.date_created >= datetime.combine(start_date, datetime.min.time()))
    
    if end_date:
        filters.append(models.Heat.date_created <= datetime.combine(end_date, datetime.max.time()))
        filters.append(models.Vibration.date_created <= datetime.combine(end_date, datetime.max.time()))
        filters.append(models.Humidity.date_created <= datetime.combine(end_date, datetime.max.time()))
    
    # Fetch filtered data
    heat_data = []
    vibration_data = []
    humidity_data = []
    
    if filters and (start_date or end_date):
        heat_query = db.query(models.Heat).filter(
            models.Heat.device_id == device.device_name
        )
        vibration_query = db.query(models.Vibration).filter(
            models.Vibration.device_id == device.device_name
        )
        humidity_query = db.query(models.Humidity).filter(
            models.Humidity.device_id == device.device_name
        )
        
        if start_date:
            heat_query = heat_query.filter(models.Heat.date_created >= datetime.combine(start_date, datetime.min.time()))
            vibration_query = vibration_query.filter(models.Vibration.date_created >= datetime.combine(start_date, datetime.min.time()))
            humidity_query = humidity_query.filter(models.Humidity.date_created >= datetime.combine(start_date, datetime.min.time()))
        
        if end_date:
            heat_query = heat_query.filter(models.Heat.date_created <= datetime.combine(end_date, datetime.max.time()))
            vibration_query = vibration_query.filter(models.Vibration.date_created <= datetime.combine(end_date, datetime.max.time()))
            humidity_query = humidity_query.filter(models.Humidity.date_created <= datetime.combine(end_date, datetime.max.time()))
        
        heat_data = heat_query.order_by(models.Heat.date_created).all()
        vibration_data = vibration_query.order_by(models.Vibration.date_created).all()
        humidity_data = humidity_query.order_by(models.Humidity.date_created).all()
    else:
        heat_data = db.query(models.Heat).filter(models.Heat.device_id == device.device_name).order_by(models.Heat.date_created).all()
        vibration_data = db.query(models.Vibration).filter(models.Vibration.device_id == device.device_name).order_by(models.Vibration.date_created).all()
        humidity_data = db.query(models.Humidity).filter(models.Humidity.device_id == device.device_name).order_by(models.Humidity.date_created).all()
    
    return {
        "device_id": device.id,
        "device_name": device.device_name,
        "device_zone": device.device_zone,
        "temperature": heat_data,
        "vibration": vibration_data,
        "humidity": humidity_data,
        "filter_dates": {
            "start_date": start_date,
            "end_date": end_date
        }
    }



