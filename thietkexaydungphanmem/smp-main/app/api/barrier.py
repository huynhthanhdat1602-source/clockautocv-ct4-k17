from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import BarrierControlRequest, BarrierControlResponse
from app.services.barrier_service import open_barrier_gate, close_barrier_gate

router = APIRouter(prefix="/api/v1/barrier", tags=["5. Barrier Gate Control"])


@router.post("/control", response_model=BarrierControlResponse, summary="Step 5: Nếu xác nhận kết quả gửi API mở barier")
def control_barrier_gate(payload: BarrierControlRequest, db: Session = Depends(get_db)):
    """
    Step 5: Issue command to barrier gate controller (OPEN or CLOSE).
    """
    action = payload.action.upper()
    if action == "OPEN":
        result = open_barrier_gate(payload.session_id, db, auto_triggered=False)
    elif action == "CLOSE":
        result = close_barrier_gate(payload.session_id, db)
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Must be 'OPEN' or 'CLOSE'.")

    return result
