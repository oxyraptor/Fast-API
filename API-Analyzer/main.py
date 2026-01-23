from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from db.sessions import engine, Base
from models import request_log
from core.middleware import request_tracking_middleware
from api.routes.items import router as items_router
from api.routes.analytics import router as analytics_router



Base.metadata.create_all(bind=engine)



app = FastAPI(title="APex", version="0.1", description="API-Analyzer")

from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(items_router)
app.include_router(analytics_router)
@app.get("/")
async def get_msg():
    return FileResponse("static/index.html")

@app.middleware("http")
async def track_request(request, call_next):
    return await request_tracking_middleware(request, call_next)

