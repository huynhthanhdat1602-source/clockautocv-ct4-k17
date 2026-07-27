import os
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app.config import CAPTURES_DIR, BASE_DIR
from app.api import rfid, camera, processing, barrier, logs

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Parking Barrier Control System API",
    description="Python system implementing RFID API -> Camera -> Async Image Processing Server -> Barrier Gate Control Workflow.",
    version="1.0.0"
)

# Enable CORS for API clients & Barrier controllers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files & Templates
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "app" / "static")), name="static")
app.mount("/static/captures", StaticFiles(directory=str(CAPTURES_DIR)), name="captures")
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))

# Include Routers
app.include_router(rfid.router)
app.include_router(camera.router)
app.include_router(processing.router)
app.include_router(barrier.router)
app.include_router(logs.router)


@app.get("/", summary="Web Dashboard UI")
def render_dashboard(request: Request):
    """
    Renders the live monitoring dashboard UI.
    """
    return templates.TemplateResponse(request=request, name="index.html")
