import cv2
from ultralytics import YOLO

model = YOLO("yolov8n.pt")
video_path = r"mvideo.mp4"
video_path1 = r"plate_test.mp4"

cap = cv2.VideoCapture(video_path)
unique_vehicles = set()
vehicle_count = 0
max_id = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break
   
    results = model.track(frame, persist=True, verbose=False)

    if results[0].boxes is None or results[0].boxes.id is None:
        continue

    boxes = results[0].boxes.xyxy
    ids = results[0].boxes.id
    classes = results[0].boxes.cls


  

    for box, track_id, cls in zip(boxes, ids, classes):
        x1, y1, x2, y2 = map(int, box)
        track_id = int(track_id)
        label = model.names[int(cls)]
        w, h = frame.shape[1], frame.shape[0]
        # h,w = frame.shape[:2]
        # y_line = int(h*0.5)
        # line_boundary = w//2
        # cv2.rectangle(frame,(0,0),(w//2,h),(255,0,0),1)

        

    
        
        
        

        if label not in ["car", "motorcycle", "bus", "truck"]:
            continue

        color = (0, 255, 0)

        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
         # if cx < line_boundary and cy < line_y:

        # if cx <= frame.shape[1] // 2:
        #     continue
        # cv2.rectangle(frame, (w//2, 0), (w//2, h), (255, 0, 0), 1)
        # color = (0, 255, 0) if track_id % 2 == 0 else (255, 0, 0)
        area = (x2 - x1) * (y2 - y1)
        if area > 2000:
            continue
        
      
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame,f"{label}, ID: {track_id}",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        
        

        cv2.circle(frame, (cx, cy), 4, (255, 0, 0), -1)
        unique_vehicles.add(track_id)
        vehicle_count = len(unique_vehicles)
        if vehicle_count>10:
            cv2.putText(frame, "Traffic Jam Detected",
                        (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 0, 255),
                        2)
        # mid_line_y = h // 2
        # cv2.line(frame, (0, mid_line_y), (w, mid_line_y), (0, 0, 255), 3)
    # hiển thị count
    cv2.putText(frame, f"Count: {vehicle_count}",
                (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 0, 0),
                2)
    cv2.imshow("Vehicle Counting", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break
cap.release()
cv2.destroyAllWindows()