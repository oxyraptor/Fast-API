from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.sessions import SessionLocal
from services.analytics_service import (
    get_most_used_endpoints,
    get_error_rate,
    get_requests_per_minute,
    get_average_response_time
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
@router.get("/most-used")
def most_used_endpoints(db: Session = Depends(get_db)):
    results = get_most_used_endpoints(db)
    return [
        {
            "endpoint": row[0],
            "count": row[1]
        }
        for row in results
    ]



@router.get("/error-rate")
def error_rate(db: Session = Depends(get_db)):
    return {"error_rate_percent": get_error_rate(db)}


@router.get("/requests-per-minute")
def requests_per_minute(db: Session = Depends(get_db)):
    results = get_requests_per_minute(db)
    return [
        {
            "minute": row[0],
            "count": row[1]
        }
        for row in results
    ]



@router.get("/avg-response-time")
def avg_response_time(db: Session = Depends(get_db)):
    return {"avg_response_time_ms": get_average_response_time(db)}
