from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from db.sessions import Base

class RequestLog(Base):
    __tablename__ = "request_log"
    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String(100), nullable=False)
    method = Column(String(100),nullable=False)
    status_code = Column(Integer, nullable=False)
    response_time = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

