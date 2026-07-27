from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import AccessLogSchema
from app.models import AccessLog
from app.config import REGISTERED_VEHICLES

router = APIRouter(prefix="/api/v1", tags=["System Monitoring & Logs"])


@router.get("/logs", response_model=List[AccessLogSchema], summary="Get activity logs")
def get_access_logs(limit: int = 50, db: Session = Depends(get_db)):
    logs = db.query(AccessLog).order_by(AccessLog.id.desc()).limit(limit).all()
    return logs


@router.delete("/logs", summary="Clear all activity logs")
def clear_access_logs(db: Session = Depends(get_db)):
    db.query(AccessLog).delete()
    db.commit()
    return {"message": "All access logs cleared successfully."}


@router.get("/vehicles", summary="Get registered vehicles dictionary")
def get_registered_vehicles():
    return REGISTERED_VEHICLES
