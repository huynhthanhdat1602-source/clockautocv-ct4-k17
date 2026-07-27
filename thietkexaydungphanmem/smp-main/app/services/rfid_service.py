import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import AccessLog, VerificationStatus, BarrierState
from app.config import REGISTERED_VEHICLES


def process_rfid_scan(rfid_code: str, db: Session):
    session_id = f"SESS-{uuid.uuid4().hex[:8].upper()}"
    
    vehicle_info = REGISTERED_VEHICLES.get(rfid_code)
    registered_plate = vehicle_info["plate"] if vehicle_info else None
    owner_name = vehicle_info["owner"] if vehicle_info else None
    is_active = vehicle_info["status"] == "active" if vehicle_info else False

    if not vehicle_info:
        msg = f"RFID card '{rfid_code}' is not registered in system."
        ver_status = VerificationStatus.UNAUTHORIZED.value
    elif not is_active:
        msg = f"RFID card '{rfid_code}' belongs to {owner_name} but is BLOCKED."
        ver_status = VerificationStatus.UNAUTHORIZED.value
    else:
        msg = f"RFID card '{rfid_code}' scanned successfully. Registered owner: {owner_name} ({registered_plate})."
        ver_status = VerificationStatus.PENDING.value

    log_entry = AccessLog(
        session_id=session_id,
        rfid_code=rfid_code,
        registered_plate=registered_plate,
        timestamp=datetime.utcnow(),
        verification_status=ver_status,
        barrier_state=BarrierState.CLOSED.value,
        message=msg
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)

    return {
        "session_id": session_id,
        "rfid_code": rfid_code,
        "timestamp": log_entry.timestamp,
        "registered_plate": registered_plate,
        "owner_name": owner_name,
        "status": "VALID" if is_active else "INVALID",
        "message": msg
    }
