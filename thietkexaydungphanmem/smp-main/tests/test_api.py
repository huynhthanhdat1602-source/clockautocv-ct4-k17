import time
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield


def test_full_workflow_valid_card():
    # 1. RFID scan
    rfid_resp = client.post("/api/v1/rfid/scan", json={"rfid_code": "RFID-889900"})
    assert rfid_resp.status_code == 200
    rfid_data = rfid_resp.json()
    assert rfid_data["status"] == "VALID"
    session_id = rfid_data["session_id"]

    # 2. Camera capture
    cam_resp = client.post("/api/v1/camera/capture", json={"session_id": session_id})
    assert cam_resp.status_code == 200
    cam_data = cam_resp.json()
    assert "image_url" in cam_data

    # 3. Async process
    proc_resp = client.post("/api/v1/process-image/async", json={
        "session_id": session_id,
        "rfid_code": "RFID-889900",
        "image_url": cam_data["image_url"]
    })
    assert proc_resp.status_code == 202
    task_id = proc_resp.json()["task_id"]

    # 4 & 5. Poll task completion
    for _ in range(10):
        time.sleep(0.4)
        task_resp = client.get(f"/api/v1/tasks/{task_id}")
        assert task_resp.status_code == 200
        task_data = task_resp.json()
        if task_data["status"] == "COMPLETED":
            break

    assert task_data["status"] == "COMPLETED"
    assert task_data["verification_status"] == "MATCH"
    assert task_data["barrier_state"] == "OPEN"


def test_invalid_unregistered_rfid():
    rfid_resp = client.post("/api/v1/rfid/scan", json={"rfid_code": "INVALID-CARD"})
    assert rfid_resp.status_code == 200
    data = rfid_resp.json()
    assert data["status"] == "INVALID"


def test_get_dashboard():
    response = client.get("/")
    assert response.status_code == 200
    assert "Hệ Thống Kiểm Soát Barrier" in response.text
