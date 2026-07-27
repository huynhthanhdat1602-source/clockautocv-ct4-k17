from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import RFIDScanRequest, RFIDScanResponse
from app.services.rfid_service import process_rfid_scan

router = APIRouter(prefix="/api/v1/rfid", tags=["1. RFID Signal"])


@router.post("/scan", response_model=RFIDScanResponse, summary="Step 1: Nhận tín hiệu từ RFID thông qua API")
def scan_rfid(payload: RFIDScanRequest, db: Session = Depends(get_db)):
    """
    Step 1: Receive RFID tap signal from reader via API endpoint.
    Creates a new tracking session ID.
    """
    if not payload.rfid_code.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="RFID code cannot be empty."
        )
    result = process_rfid_scan(payload.rfid_code, db)
    return result
