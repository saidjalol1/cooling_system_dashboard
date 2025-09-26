from sqlalchemy import Column, Integer, String, ForeignKey, Text, Table, Boolean, Float, DateTime, Numeric, Enum
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from config.database import Base, current_time


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)


