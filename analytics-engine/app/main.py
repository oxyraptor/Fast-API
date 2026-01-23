from fastapi import FastAPI
from .api.routes import router

app = FastAPI(title="Analytics as a service", version= "0.1.0")

from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="app/static", html=True), name="static")

@app.get("/")
def get_msg():
    return {"API is wroking"}

app.include_router(router)

