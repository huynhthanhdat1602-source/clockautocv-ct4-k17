let currentSessionId = null;
let currentTaskId = null;
let currentRfidCode = null;
let currentImageUrl = null;

document.addEventListener("DOMContentLoaded", () => {
    loadLogs();
    setInterval(loadLogs, 3000);

    document.getElementById("rfidSelect").addEventListener("change", (e) => {
        const val = e.target.value;
        if (val) {
            document.getElementById("rfidInput").value = val;
        }
    });
});

async function runFullWorkflow() {
    const rfidCode = document.getElementById("rfidInput").value.trim();
    if (!rfidCode) {
        alert("Vui lòng nhập hoặc chọn mã RFID!");
        return;
    }

    try {
        // Step 1: RFID Scan
        updateStepActive(1);
        logTerminal(">>> [STEP 1] Gửi API nhận tín hiệu RFID...");
        const rfidRes = await fetch("/api/v1/rfid/scan", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ rfid_code: rfidCode })
        });
        const rfidData = await rfidRes.json();
        currentSessionId = rfidData.session_id;
        currentRfidCode = rfidCode;
        logTerminal(`[STEP 1 SUCCESS] Session: ${currentSessionId} | Owner: ${rfidData.owner_name || 'N/A'}`);

        // Step 2: Camera Capture
        updateStepActive(2);
        logTerminal(">>> [STEP 2] Camera chụp hình vehicle...");
        const customPlate = document.getElementById("customPlateInput").value.trim() || null;
        const camRes = await fetch("/api/v1/camera/capture", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: currentSessionId, custom_plate: customPlate })
        });
        const camData = await camRes.json();
        currentImageUrl = camData.image_url;
        document.getElementById("cameraImg").src = currentImageUrl + "?t=" + new Date().getTime();
        document.getElementById("cameraPlaceholder").style.display = "none";
        document.getElementById("cameraImg").style.display = "block";
        logTerminal(`[STEP 2 SUCCESS] Captured Image URL: ${currentImageUrl}`);

        // Step 3: Async Image Processing
        updateStepActive(3);
        logTerminal(">>> [STEP 3] Gửi hình ảnh về Server xử lý thông qua Async API...");
        const procRes = await fetch("/api/v1/process-image/async", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                session_id: currentSessionId,
                rfid_code: currentRfidCode,
                image_url: currentImageUrl
            })
        });
        const procData = await procRes.json();
        currentTaskId = procData.task_id;
        logTerminal(`[STEP 3 QUEUED] Task ID: ${currentTaskId}. Server is processing asynchronously...`);

        // Step 4: Poll Async Task Status
        updateStepActive(4);
        pollTaskStatus(currentTaskId);

    } catch (err) {
        logTerminal(`[ERROR] ${err.message}`);
    }
}

async function pollTaskStatus(taskId) {
    let attempts = 0;
    const interval = setInterval(async () => {
        attempts++;
        try {
            const res = await fetch(`/api/v1/tasks/${taskId}`);
            const data = await res.json();

            if (data.status === "COMPLETED") {
                clearInterval(interval);
                logTerminal(`[STEP 4 COMPLETE] Result: ${data.verification_status} | OCR Plate: ${data.recognized_plate}`);
                
                // Step 5: Check Barrier status
                updateStepActive(5);
                if (data.verification_status === "MATCH" && data.barrier_state === "OPEN") {
                    setBarrierArm(true);
                    logTerminal(">>> [STEP 5 SUCCESS] API mở barier thành công! Barrier Gate IS OPEN.");
                } else {
                    setBarrierArm(false);
                    logTerminal(`>>> [STEP 5 DENIED] Verification status: ${data.verification_status}. Barrier Gate remains CLOSED.`);
                }
                loadLogs();
            } else {
                logTerminal(`[STEP 4 WAITING] Task ${taskId} processing... (attempt ${attempts})`);
            }
        } catch (err) {
            clearInterval(interval);
            logTerminal(`[ERROR Polling] ${err.message}`);
        }
    }, 600);
}

function updateStepActive(stepNum) {
    for (let i = 1; i <= 5; i++) {
        const el = document.getElementById(`stepBox${i}`);
        if (el) {
            if (i === stepNum) el.classList.add("active");
            else el.classList.remove("active");
        }
    }
}

function setBarrierArm(isOpen) {
    const arm = document.getElementById("barrierArm");
    const statusText = document.getElementById("barrierStatusText");
    if (isOpen) {
        arm.classList.add("open");
        statusText.innerText = "GATE OPEN";
        statusText.style.color = "var(--accent-green)";
    } else {
        arm.classList.remove("open");
        statusText.innerText = "GATE CLOSED";
        statusText.style.color = "var(--accent-red)";
    }
}

async function manualBarrier(action) {
    if (!currentSessionId) {
        currentSessionId = "MANUAL-OVERRIDE";
    }
    const res = await fetch("/api/v1/barrier/control", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: currentSessionId, action: action })
    });
    const data = await res.json();
    setBarrierArm(action === "OPEN" && data.success);
    logTerminal(`[MANUAL BARRIER] ${data.message}`);
    loadLogs();
}

async function clearLogs() {
    if (!confirm("Bạn có chắc chắn muốn xóa toàn bộ lịch sử log không?")) {
        return;
    }
    try {
        const res = await fetch("/api/v1/logs", { method: "DELETE" });
        const data = await res.json();
        logTerminal(`[SYSTEM] ${data.message}`);
        loadLogs();
    } catch (e) {
        console.error("Failed to clear logs", e);
    }
}

async function loadLogs() {
    try {
        const res = await fetch("/api/v1/logs");
        const logs = await res.json();
        const tbody = document.getElementById("logsTbody");
        tbody.innerHTML = "";

        const filterVal = document.getElementById("logFilterSelect") ? document.getElementById("logFilterSelect").value : "ALL";

        logs.forEach(log => {
            if (filterVal !== "ALL" && log.verification_status !== filterVal) {
                return;
            }

            const tr = document.createElement("tr");
            const dateStr = new Date(log.timestamp).toLocaleTimeString();
            let badgeClass = "badge-pending";
            let icon = "⌛";

            if (log.verification_status === "MATCH") {
                badgeClass = "badge-match";
                icon = "✅";
            } else if (log.verification_status === "UNMATCHED") {
                badgeClass = "badge-unmatched";
                icon = "⚠️";
            } else if (log.verification_status === "UNAUTHORIZED") {
                badgeClass = "badge-unauthorized";
                icon = "❌";
            }

            const barrierColor = log.barrier_state === "OPEN" ? "var(--accent-green)" : "var(--accent-red)";
            const regPlateDisplay = log.registered_plate || '—';
            const recPlateDisplay = log.recognized_plate || '—';

            tr.innerHTML = `
                <td><code>${log.session_id}</code></td>
                <td><strong>${log.rfid_code}</strong></td>
                <td><span style="color: var(--accent-blue); font-weight: 600;">${regPlateDisplay}</span></td>
                <td><span style="color: #f1f5f9; font-weight: 600;">${recPlateDisplay}</span></td>
                <td><span class="status-badge ${badgeClass}">${icon} ${log.verification_status}</span></td>
                <td><strong style="color: ${barrierColor}">${log.barrier_state}</strong></td>
                <td>${dateStr}</td>
                <td style="font-size: 0.8rem; color: var(--text-secondary);">${log.message || '—'}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        console.error("Failed to load logs", e);
    }
}

function logTerminal(msg) {
    const term = document.getElementById("terminalLog");
    const line = document.createElement("div");
    line.textContent = `[${new Date().toLocaleTimeString()}] ${msg}`;
    term.appendChild(line);
    term.scrollTop = term.scrollHeight;
}
