from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from config import database
from shemas import models, schemas



users = APIRouter(
    tags=["Users"]
)

@users.post("/users/create")
async def create_user(user_schema: schemas.User, db: Session = Depends(database.get_db)):
    user = models.User(**user_schema.model_dump())

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message":"user created successfullty", "data":user}
