import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CAPTURES_DIR = DATA_DIR / "captures"

DATA_DIR.mkdir(exist_ok=True)
CAPTURES_DIR.mkdir(exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'parking_system.db'}")

# Simulated Registered RFID Tags and License Plates
REGISTERED_VEHICLES = {
    "RFID-889900": {"plate": "30A-888.88", "owner": "Nguyen Van A", "status": "active"},
    "RFID-112233": {"plate": "29B-123.45", "owner": "Tran Thi B", "status": "active"},
    "RFID-556677": {"plate": "51G-999.99", "owner": "Le Van C", "status": "active"},
    "RFID-778899": {"plate": "43A-678.90", "owner": "Pham Van D", "status": "blocked"},
}
