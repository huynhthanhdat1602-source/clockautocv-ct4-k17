"""
E2E Python Workflow Simulator
Simulates:
1. RFID Tag scan signal via API
2. Camera image capture
3. Async image processing request to server
4. Polling result from server
5. Barrier open gate confirmation
"""
import sys
import time
import httpx

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8000"


def run_simulation(rfid_code: str = "RFID-889900", custom_plate: str = None):
    print("=" * 60)
    print(f"🚀 STARTING WORKFLOW SIMULATION FOR RFID: {rfid_code}")
    print("=" * 60)

    client = httpx.Client(base_url=BASE_URL, timeout=10.0)

    # Step 1: RFID Signal via API
    print("\n[Step 1] Nhận tín hiệu từ RFID thông qua API...")
    rfid_res = client.post("/api/v1/rfid/scan", json={"rfid_code": rfid_code})
    if rfid_res.status_code != 200:
        print(f"❌ Step 1 Failed: {rfid_res.text}")
        return
    rfid_data = rfid_res.json()
    session_id = rfid_data["session_id"]
    print(f"✅ [Step 1 SUCCESS] Session ID: {session_id} | Status: {rfid_data['status']}")

    # Step 2: Camera Capture
    print("\n[Step 2] Camera chụp hình...")
    cam_res = client.post("/api/v1/camera/capture", json={
        "session_id": session_id,
        "custom_plate": custom_plate
    })
    if cam_res.status_code != 200:
        print(f"❌ Step 2 Failed: {cam_res.text}")
        return
    cam_data = cam_res.json()
    image_url = cam_data["image_url"]
    print(f"✅ [Step 2 SUCCESS] Image captured: {image_url}")

    # Step 3: Send image to async server via API
    print("\n[Step 3] Gửi hình ảnh về server xử lý thông qua API. API bất đồng bộ...")
    async_res = client.post("/api/v1/process-image/async", json={
        "session_id": session_id,
        "rfid_code": rfid_code,
        "image_url": image_url
    })
    if async_res.status_code != 202:
        print(f"❌ Step 3 Failed: {async_res.text}")
        return
    async_data = async_res.json()
    task_id = async_data["task_id"]
    print(f"✅ [Step 3 ACCEPTED] Task ID: {task_id} queued on async server.")

    # Step 4: Server processes and returns result to client
    print("\n[Step 4] Server xử lý và trả kết quả về client (Máy tính điều khiển barier)...")
    completed = False
    for attempt in range(1, 10):
        time.sleep(0.5)
        task_res = client.get(f"/api/v1/tasks/{task_id}")
        task_data = task_res.json()
        print(f"   ⌛ Polling task status (attempt {attempt}): {task_data['status']} - {task_data['verification_status']}")
        if task_data["status"] == "COMPLETED":
            completed = True
            break

    if not completed:
        print("❌ Step 4 Timeout waiting for async server completion.")
        return

    print(f"✅ [Step 4 SUCCESS] Recognized Plate: {task_data['recognized_plate']} | Verification: {task_data['verification_status']}")

    # Step 5: Check Barrier state
    print("\n[Step 5] Nếu xác nhận kết quả gửi API mở barier...")
    print(f"🏁 Final Barrier State: {task_data['barrier_state']}")
    print(f"💬 Message: {task_data['message']}")
    print("=" * 60)


if __name__ == "__main__":
    test_rfid = sys.argv[1] if len(sys.argv) > 1 else "RFID-889900"
    run_simulation(test_rfid)
