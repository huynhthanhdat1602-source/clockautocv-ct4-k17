from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import CameraCaptureRequest, CameraCaptureResponse
from app.services.camera_service import capture_camera_snapshot

router = APIRouter(prefix="/api/v1/camera", tags=["2. Camera Capture"])


@router.post("/capture", response_model=CameraCaptureResponse, summary="Step 2: Camera chụp hình")
def trigger_camera_capture(payload: CameraCaptureRequest, db: Session = Depends(get_db)):
    """
    Step 2: Trigger vehicle image capture upon receiving RFID signal.
    """
    result = capture_camera_snapshot(payload.session_id, payload.custom_plate, db)
    return result
