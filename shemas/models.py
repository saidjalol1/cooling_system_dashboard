from sqlalchemy import Column, Integer, String, ForeignKey, Text, Table, Boolean, Float, DateTime, Numeric, Enum
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from config.database import Base, current_time


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)


class Device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True, index=True)

    device_name = Column(String)
    device_zone = Column(String)

    date_created = Column(DateTime, default=current_time)


    temperature = relationship("Heat", back_populates="device")
    vibration = relationship("Vibration", back_populates="device")
    

class Heat(Base):
    __tablename__ = "heat"

    id = Column(Integer, primary_key=True, index=True)

    heat = Column(Float)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    date_created = Column(DateTime, default=current_time)

     
    device = relationship("Device", back_populates="temperature")



class Vibration(Base):
    __tablename__ = "vibrations"

    id = Column(Integer, primary_key=True, index=True)

    vibration = Column(Float)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    date_created = Column(DateTime, default=current_time)


    device = relationship("Device", back_populates="vibration")


