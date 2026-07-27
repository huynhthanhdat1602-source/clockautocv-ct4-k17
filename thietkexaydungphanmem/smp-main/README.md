# Parking Barrier Control System (Python)

Dự án Python xây dựng hệ thống kiểm soát barrier đỗ xe tự động dựa theo đúng workflow trong sơ đồ:
1. **Nhận tín hiệu từ RFID thông qua API** (`POST /api/v1/rfid/scan`)
2. **Camera chụp hình** (`POST /api/v1/camera/capture`)
3. **Gửi hình ảnh về server xử lý thông qua API (API bất đồng bộ)** (`POST /api/v1/process-image/async`)
4. **Server xử lý và trả kết quả về client (Máy tính điều khiển barier)** (`GET /api/v1/tasks/{task_id}`)
5. **Nếu xác nhận kết quả gửi API mở barier** (`POST /api/v1/barrier/control`)
6. **Kết thúc**

---

## 🛠 Hướng Dẫn Cài Đặt & Chạy Dự Án

### 1. Khởi tạo môi trường venv & Cài đặt thư viện
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Khởi chạy Uvicorn Server (API + Web Dashboard)
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- Web Dashboard Giám Sát: http://localhost:8000
- Open API Docs (Swagger UI): http://localhost:8000/docs

### 3. Chạy File Mô Phỏng (CLI Workflow Simulator)
Trong cửa sổ terminal thứ 2:
```bash
source .venv/bin/activate
python simulator.py RFID-889900
```

### 4. Chạy Unit Tests
```bash
pytest
```

---

## 📁 Thư Mục Dự Án

```
smp/
├── app/
│   ├── api/             # API Routers tương ứng 5 bước workflow
│   ├── services/        # Logic RFID, Camera, Async Server Processing, Barrier Control
│   ├── config.py        # Cấu hình & danh sách thẻ mẫu
│   ├── database.py      # SQLAlchemy & SQLite setup
│   ├── models.py        # Database models (AccessLog, RegisteredVehicle)
│   ├── schemas.py       # Pydantic Schemas
│   ├── main.py          # FastAPI Entry Point
│   ├── static/          # CSS & JS Dashboard
│   └── templates/       # UI Dashboard index.html
├── data/
│   └── captures/        # Ảnh chụp camera sinh tự động
├── tests/               # Pytest Automated Integration Tests
├── simulator.py         # Kịch bản mô phỏng Python E2E
├── requirements.txt
└── README.md
```
