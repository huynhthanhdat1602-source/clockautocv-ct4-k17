import cv2 as cv
import easyocr

video_path = r"C:\Users\Admin\Desktop\CV-CT4-K17\plate2.mp4"
cap = cv.VideoCapture(video_path)

def detect_plate(img):
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    _, binary = cv.threshold(gray, 128, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    clean_img = cv.fastNlMeansDenoising(binary, h=10)
    edges = cv.Canny(clean_img, 20, 150)
    keypoints = cv.getStructuringElement(cv.MORPH_RECT, (3,3))
    close_box = cv.morphologyEx(edges, cv.MORPH_CLOSE, keypoints)
    contours, _ = cv.findContours(close_box.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    plates = []
    img_size = img.shape[0] * img.shape[1]
    for cnt in contours:
        x, y, w, h = cv.boundingRect(cnt)
        aspect_ratio = w / h
        area_ratio = (w * h) / img_size
        if (1.0 < aspect_ratio < 6.0) and (0.005 < area_ratio < 0.5):
            plates.append((x, y, w, h))
            cv.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return plates

def crop_plate(img, x, y, w, h, pad=5):
    x1 = max(0, x - pad)
    y1 = max(0, y - pad)
    x2 = min(img.shape[1], x + w + pad)
    y2 = min(img.shape[0], y + h + pad)
    return img[y1:y2, x1:x2]

def ocr_plate(img, plates):
    results = []
    reader = easyocr.Reader(["en"], gpu=False)
    for x, y, w, h in plates:
        plate_img = crop_plate(img, x, y, w, h)
        if plate_img.size == 0:
            continue
        gimg = cv.cvtColor(plate_img, cv.COLOR_BGR2GRAY)
        _, binary = cv.threshold(gimg, 128, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
        ocr_results = reader.readtext(binary, allowlist="0123456789ABCDEFGHKLMNPQRSTUVXY", detail=1)
        for bbox, text, conf in ocr_results:
            results.append((text, conf))
            # Vẽ text lên ảnh gốc
            cv.putText(img, f"{text} ({conf:.2f})", (x, y-10), 
                      cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    return results
frame_count = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame_count += 1
    if frame_count % 10 != 0:  # Chỉ xử lý mỗi 10 khung hình để tăng tốc
     frame_copy = frame.copy()
    plates = detect_plate(frame_copy)
    ocr_results = ocr_plate(frame_copy, plates)
    
    # In kết quả OCR
    for text, conf in ocr_results:
        print(f"Phát hiện biển số: {text} (độ tin cậy: {conf:.2f})")
    
    cv.imshow("video", frame_copy)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()