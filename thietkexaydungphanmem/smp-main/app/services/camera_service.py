import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from sqlalchemy.orm import Session
from app.config import CAPTURES_DIR, REGISTERED_VEHICLES
from app.models import AccessLog


def create_simulated_license_plate_image(plate_text: str, filename: str) -> str:
    """Generate a clean synthetic camera capture image with a license plate."""
    width, height = 640, 480
    image = Image.new("RGB", (width, height), color=(40, 44, 52))
    draw = ImageDraw.Draw(image)

    # Draw simulated car body
    draw.rectangle([100, 150, 540, 420], fill=(24, 28, 36), outline=(80, 90, 100), width=3)
    draw.rectangle([160, 170, 480, 260], fill=(15, 18, 24), outline=(60, 70, 80), width=2)  # Windshield
    
    # Draw headlights
    draw.ellipse([120, 290, 180, 330], fill=(255, 235, 150), outline=(200, 180, 100))
    draw.ellipse([460, 290, 520, 330], fill=(255, 235, 150), outline=(200, 180, 100))

    # Draw License Plate Frame
    draw.rectangle([210, 320, 430, 390], fill=(255, 255, 255), outline=(0, 0, 0), width=4)
    draw.rectangle([215, 325, 425, 385], fill=(250, 250, 250), outline=(0, 50, 150), width=2)

    # Draw Text on License Plate
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    # Draw text in center
    draw.text((250, 345), plate_text, fill=(0, 0, 0), font=font)
    
    # Add timestamp overlay at top left
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    draw.text((15, 15), f"CAM-01 FRONT GATE | {timestamp_str}", fill=(0, 255, 128), font=font)

    filepath = CAPTURES_DIR / filename
    image.save(filepath, format="JPEG")
    return f"/static/captures/{filename}"


def capture_camera_snapshot(session_id: str, custom_plate: str | None, db: Session) -> dict:
    log_entry = db.query(AccessLog).filter(AccessLog.session_id == session_id).first()
    
    plate_to_render = custom_plate
    if not plate_to_render and log_entry:
        veh_info = REGISTERED_VEHICLES.get(log_entry.rfid_code)
        plate_to_render = veh_info["plate"] if veh_info else "30A-999.99"
    elif not plate_to_render:
        plate_to_render = "30A-888.88"

    filename = f"cap_{session_id}.jpg"
    image_url = create_simulated_license_plate_image(plate_to_render, filename)

    if log_entry:
        log_entry.image_url = image_url
        log_entry.recognized_plate = plate_to_render
        log_entry.message = f"Camera snapshot captured plate '{plate_to_render}' for session {session_id}."
        db.commit()

    return {
        "session_id": session_id,
        "image_url": image_url,
        "timestamp": datetime.utcnow()
    }
