import asyncio
import time
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import AccessLog, VerificationStatus, BarrierState
from app.config import REGISTERED_VEHICLES
from app.services.barrier_service import open_barrier_gate


async def async_process_image_task(task_id: str, session_id: str, rfid_code: str, image_url: str):
    """
    Simulates asynchronous image processing server (ALPR / License Plate Recognition OCR).
    Steps:
    1. Async background delay (1.5 seconds) simulating AI image analysis.
    2. Extract plate number from image metadata / session.
    3. Validate against RFID registration database.
    4. Return processing result to barrier controller client.
    5. If verification SUCCESS (MATCH), issue API call to open barrier!
    """
    await asyncio.sleep(1.5)  # Simulate AI deep learning inference time

    db: Session = SessionLocal()
    try:
        log_entry = db.query(AccessLog).filter(AccessLog.session_id == session_id).first()
        if not log_entry:
            return

        vehicle_info = REGISTERED_VEHICLES.get(rfid_code)

        # Extract plate from captured image in session (or fallback to registration info)
        recognized_plate = log_entry.recognized_plate or (vehicle_info["plate"] if vehicle_info else "UNKNOWN-PLATE")
        ocr_confidence = 0.98 if (vehicle_info and recognized_plate == vehicle_info["plate"]) else 0.85

        log_entry.recognized_plate = recognized_plate
        log_entry.ocr_confidence = ocr_confidence
        log_entry.task_id = task_id

        if not vehicle_info:
            log_entry.verification_status = VerificationStatus.UNAUTHORIZED.value
            log_entry.barrier_state = BarrierState.DENIED.value
            log_entry.message = f"Async Server: Card '{rfid_code}' unauthorized. Plate recognized: {recognized_plate}."
        elif vehicle_info["status"] != "active":
            log_entry.verification_status = VerificationStatus.UNAUTHORIZED.value
            log_entry.barrier_state = BarrierState.DENIED.value
            log_entry.message = f"Async Server: Card '{rfid_code}' belongs to {vehicle_info['owner']} but is BLOCKED."
        elif recognized_plate == vehicle_info["plate"]:
            log_entry.verification_status = VerificationStatus.MATCH.value
            log_entry.message = f"Async Server: SUCCESS! License plate '{recognized_plate}' matches RFID '{rfid_code}' ({vehicle_info['owner']})."
        else:
            log_entry.verification_status = VerificationStatus.UNMATCHED.value
            log_entry.barrier_state = BarrierState.DENIED.value
            log_entry.message = f"Async Server: MISMATCH! Recognized plate '{recognized_plate}' DOES NOT MATCH registered plate '{vehicle_info['plate']}'."

        db.commit()

        # Step 5 in workflow: If confirmed result (MATCH), trigger API to open barrier gate!
        if log_entry.verification_status == VerificationStatus.MATCH.value:
            open_barrier_gate(session_id, db, auto_triggered=True)

    finally:
        db.close()
