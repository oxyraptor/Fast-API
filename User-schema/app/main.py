from fastapi import FastAPI
from app.routers import users

app = FastAPI(
    title="Core FastAPI Foundations Project",
    version="1.0.0"
)

app.include_router(users.router)

@app.get("/")
def health_check():
    return {"status": "API is On bete"}


