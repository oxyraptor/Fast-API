from sqlalchemy.orm import Session
from sqlalchemy import func
from models.request_log import RequestLog
from datetime import datetime, timedelta



def get_most_used_endpoints(db: Session, limit: int = 5):
    return (
        db.query(
            RequestLog.endpoint,
            func.count(RequestLog.id).label("request_count")
        )
        .group_by(RequestLog.endpoint)
        .order_by(func.count(RequestLog.id).desc())
        .limit(limit)
        .all()
    )


def get_error_rate(db: Session):
    total_requests = db.query(func.count(RequestLog.id)).scalar()
    error_requests = (
        db.query(func.count(RequestLog.id))
        .filter(RequestLog.status_code >= 400)
        .scalar()
    )

    if total_requests == 0:
        return 0.0

    return round((error_requests / total_requests) * 100, 2)


def get_requests_per_minute(db: Session, minutes: int = 5):
    since = datetime.utcnow() - timedelta(minutes=minutes)

    return (
        db.query(
            func.strftime("%Y-%m-%d %H:%M", RequestLog.timestamp).label("minute"),
            func.count(RequestLog.id).label("count")
        )
        .filter(RequestLog.timestamp >= since)
        .group_by("minute")
        .order_by("minute")
        .all()
    )



def get_average_response_time(db: Session):
    avg_time = db.query(func.avg(RequestLog.response_time)).scalar()
    return round(avg_time or 0, 2)
