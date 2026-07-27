from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum
from datetime import datetime
import enum
from app.database import Base


class VerificationStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    MATCH = "MATCH"
    UNMATCHED = "UNMATCHED"
    UNAUTHORIZED = "UNAUTHORIZED"
    FAILED = "FAILED"


class BarrierState(str, enum.Enum):
    CLOSED = "CLOSED"
    OPENING = "OPENING"
    OPEN = "OPEN"
    CLOSING = "CLOSING"
    DENIED = "DENIED"


class RegisteredVehicle(Base):
    __tablename__ = "registered_vehicles"

    id = Column(Integer, primary_key=True, index=True)
    rfid_code = Column(String, unique=True, index=True, nullable=False)
    plate_number = Column(String, index=True, nullable=False)
    owner_name = Column(String, nullable=False)
    status = Column(String, default="active")  # active, blocked
    created_at = Column(DateTime, default=datetime.utcnow)


class AccessLog(Base):
    __tablename__ = "access_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, nullable=False)
    rfid_code = Column(String, index=True, nullable=False)
    registered_plate = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    image_url = Column(String, nullable=True)
    recognized_plate = Column(String, nullable=True)
    ocr_confidence = Column(Float, nullable=True)
    
    verification_status = Column(String, default=VerificationStatus.PENDING.value)
    barrier_state = Column(String, default=BarrierState.CLOSED.value)
    task_id = Column(String, nullable=True)
    message = Column(String, nullable=True)
