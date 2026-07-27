import uuid
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import AsyncProcessRequest, AsyncProcessResponse, TaskStatusResponse
from app.services.image_processor import async_process_image_task
from app.models import AccessLog

router = APIRouter(prefix="/api/v1", tags=["3 & 4. Async Image Processing Server"])


@router.post(
    "/process-image/async",
    response_model=AsyncProcessResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Step 3: Gửi hình ảnh về server xử lý thông qua API. API bất đồng bộ."
)
def submit_image_processing_async(
    payload: AsyncProcessRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Step 3: Submit captured image to server for asynchronous processing (ALPR / Recognition).
    Returns 202 Accepted immediately with a unique task_id.
    """
    task_id = f"TASK-{uuid.uuid4().hex[:8].upper()}"

    log_entry = db.query(AccessLog).filter(AccessLog.session_id == payload.session_id).first()
    if log_entry:
        log_entry.task_id = task_id
        log_entry.verification_status = "PROCESSING"
        log_entry.message = f"Image submitted to async processing server (Task: {task_id})."
        db.commit()

    # Schedule asynchronous execution in background task queue
    background_tasks.add_task(
        async_process_image_task,
        task_id=task_id,
        session_id=payload.session_id,
        rfid_code=payload.rfid_code,
        image_url=payload.image_url
    )

    return {
        "task_id": task_id,
        "session_id": payload.session_id,
        "status": "QUEUED",
        "message": "Async image processing task dispatched to server queue."
    }


@router.get(
    "/tasks/{task_id}",
    response_model=TaskStatusResponse,
    summary="Step 4: Server xử lý và trả kết quả về client (Máy tính điều khiển barier)"
)
def get_processing_task_status(task_id: str, db: Session = Depends(get_db)):
    """
    Step 4: Retrieve processing status and result from processing server.
    """
    log_entry = db.query(AccessLog).filter(AccessLog.task_id == task_id).first()
    if not log_entry:
        raise HTTPException(status_code=404, detail=f"Task ID '{task_id}' not found.")

    is_completed = log_entry.verification_status not in ["PENDING", "PROCESSING"]

    return {
        "task_id": task_id,
        "session_id": log_entry.session_id,
        "rfid_code": log_entry.rfid_code,
        "status": "COMPLETED" if is_completed else "IN_PROGRESS",
        "recognized_plate": log_entry.recognized_plate,
        "ocr_confidence": log_entry.ocr_confidence,
        "verification_status": log_entry.verification_status,
        "barrier_state": log_entry.barrier_state,
        "message": log_entry.message or ""
    }
