import time
import logging
from datetime import timedelta

from fastapi import FastAPI, Request, Depends, status, HTTPException

from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from config.database import get_db
from auth import auth_main, token
from shemas.models import User, Device, Heat, Vibration, Humidity
from shemas import schemas

from api import user_routes, device_routes

app  = FastAPI()


# routes
app.include_router(user_routes.users)
app.include_router(device_routes.device)


# midlware and cors conf
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# log conf
@app.middleware("https")
async def log_request_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logging.info(f"{request.method} {request.url} - {response.status_code} - Took {process_time:.4f} seconds")
    return response


# template and static files conf
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Endpoints
@app.get("/")
async def dashboard(request: Request,db : Session = Depends(get_db)):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/detail/{id}/page")
async def detail(id: int,request: Request,db : Session = Depends(get_db)):
    data = db.query(Device).filter(Device.id == id).first()
    
    humidity = db.query(Humidity).filter(Humidity.device_id == data.device_name).all()
    vibaration = db.query(Vibration).filter(Vibration.device_id == data.device_name).all()
    temperature = db.query(Heat).filter(Heat.device_id == data.device_name).all()

    device = jsonable_encoder(data)

    device["temperature"] = jsonable_encoder(temperature)
    device["vibration"] = jsonable_encoder(vibaration)
    device["humidity"] = jsonable_encoder(humidity)
    return templates.TemplateResponse(
        "motor-detail.html",
        {"request": request, "context": device}
    )


@app.post("/token")
async def login(user_token : OAuth2PasswordRequestForm = Depends(),database : Session = Depends(get_db)):
    user = auth_main.authenticate_user(user_token.username,user_token.password, database)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Could not validated the User")
    created_token = token.create_access_token(user.username, user.id, timedelta(minutes=1000))
    return {"access_token": created_token, "token_type": "bearer","user":user}