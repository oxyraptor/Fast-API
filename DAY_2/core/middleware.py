import fastapi
import time
from datetime import datetime
from db.sessions import SessionLocal
from models.request_log import RequestLog
from fastapi import Request

async def request_tracking_middleware(request:Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time = (time.time() - start_time)*1000

    db = SessionLocal()
    try:
        log = RequestLog(
            endpoint=request.url.path,
            method=request.method,
            status_code=response.status_code,
            response_time=process_time,
            timestamp=datetime.utcnow()
        )
        db.add(log)
        db.commit()

    finally:
        db.close()

    return response

