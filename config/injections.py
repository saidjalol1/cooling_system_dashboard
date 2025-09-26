from typing import Optional, Union
from fastapi import Depends, status, HTTPException
from sqlalchemy.orm import Session
from shemas import models
from .database import get_db
from auth.auth_main import get_current_user



database_dep : Session = Depends(get_db)


async def session_manager(object, db):
    """ creating object in databse"""
    object_ = object
    db.add(object)
    db.commit()
    db.refresh(object_)
    return object_


def error_messages(error_msg):
    if "unique constraint" in error_msg:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists."
        )
    elif "not-null constraint" in error_msg:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required fields."
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error: " + error_msg
        )