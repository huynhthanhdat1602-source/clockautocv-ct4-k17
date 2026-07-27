from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List


class RFIDScanRequest(BaseModel):
    rfid_code: str


class RFIDScanResponse(BaseModel):
    session_id: str
    rfid_code: str
    timestamp: datetime
    registered_plate: Optional[str] = None
    owner_name: Optional[str] = None
    status: str
    message: str


class CameraCaptureRequest(BaseModel):
    session_id: str
    custom_plate: Optional[str] = None  # Allow overriding plate for testing/simulation


class CameraCaptureResponse(BaseModel):
    session_id: str
    image_url: str
    timestamp: datetime


class AsyncProcessRequest(BaseModel):
    session_id: str
    rfid_code: str
    image_url: str


class AsyncProcessResponse(BaseModel):
    task_id: str
    session_id: str
    status: str
    message: str


class TaskStatusResponse(BaseModel):
    task_id: str
    session_id: str
    rfid_code: str
    status: str
    recognized_plate: Optional[str] = None
    ocr_confidence: Optional[float] = None
    verification_status: str
    barrier_state: str
    message: str


class BarrierControlRequest(BaseModel):
    session_id: str
    action: str  # OPEN or CLOSE


class BarrierControlResponse(BaseModel):
    session_id: str
    barrier_state: str
    success: bool
    message: str


class AccessLogSchema(BaseModel):
    id: int
    session_id: str
    rfid_code: str
    registered_plate: Optional[str] = None
    timestamp: datetime
    image_url: Optional[str] = None
    recognized_plate: Optional[str] = None
    ocr_confidence: Optional[float] = None
    verification_status: str
    barrier_state: str
    message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
