from sqlalchemy.orm import Session
from app.models import AccessLog, BarrierState, VerificationStatus


def open_barrier_gate(session_id: str, db: Session, auto_triggered: bool = False) -> dict:
    log_entry = db.query(AccessLog).filter(AccessLog.session_id == session_id).first()
    
    if not log_entry:
        return {
            "session_id": session_id,
            "barrier_state": BarrierState.CLOSED.value,
            "success": False,
            "message": "Session not found."
        }

    # Only open if verification is MATCH or manual override
    if log_entry.verification_status == VerificationStatus.MATCH.value or not auto_triggered:
        log_entry.barrier_state = BarrierState.OPEN.value
        prefix = "[AUTO]" if auto_triggered else "[MANUAL OVERRIDE]"
        log_entry.message = f"{prefix} Barrier Gate OPEN API signal sent successfully."
        db.commit()
        return {
            "session_id": session_id,
            "barrier_state": BarrierState.OPEN.value,
            "success": True,
            "message": log_entry.message
        }
    else:
        log_entry.barrier_state = BarrierState.DENIED.value
        log_entry.message = f"Barrier Gate OPEN request DENIED due to verification status: {log_entry.verification_status}."
        db.commit()
        return {
            "session_id": session_id,
            "barrier_state": BarrierState.DENIED.value,
            "success": False,
            "message": log_entry.message
        }


def close_barrier_gate(session_id: str, db: Session) -> dict:
    log_entry = db.query(AccessLog).filter(AccessLog.session_id == session_id).first()
    if log_entry:
        log_entry.barrier_state = BarrierState.CLOSED.value
        log_entry.message = "Barrier Gate CLOSED API signal sent."
        db.commit()
        return {
            "session_id": session_id,
            "barrier_state": BarrierState.CLOSED.value,
            "success": True,
            "message": log_entry.message
        }
    return {
        "session_id": session_id,
        "barrier_state": BarrierState.CLOSED.value,
        "success": False,
        "message": "Session not found."
    }
