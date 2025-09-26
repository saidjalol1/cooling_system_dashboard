from datetime import date, datetime
from typing import Union, Optional, List
from pydantic import BaseModel, Field


# user shemas
class User(BaseModel):
    username : str
    hashed_password : str
    
    class Config:
        from_attributes = True


class UserOut(BaseModel):
    id: int


# device 
class DeviceBase(BaseModel):
    device_name : str
    device_zone : str


class VibrationBase(BaseModel):
    vibration: float
    device_id: int


class HeatBase(BaseModel):
    heat: float
    device_id: int


class Vibration(VibrationBase):
    id: int
    date_created: datetime


class Heat(HeatBase):
    id: int
    date_created: datetime


class Device(BaseModel):
    id: int
    heat: List[Heat] = Field(default_factory=list)
    vibration: List[Vibration] = Field(default_factory=list)

