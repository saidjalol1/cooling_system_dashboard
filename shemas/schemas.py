from datetime import date, datetime
from typing import Union, Optional
from pydantic import BaseModel


# user shemas
class User(BaseModel):
    username : str
    hashed_password : str
    
    class Config:
        from_attributes = True


class UserOut(BaseModel):
    id: int