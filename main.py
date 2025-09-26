from fastapi import FastAPI



app  = FastAPI()


@app.get("/api")
async def welcome_page():
    return {"message":"Welcome to the Dashboard of cooling system"}


