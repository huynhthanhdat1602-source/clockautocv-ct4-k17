import matplotlib.pyplot as plt
import numpy as np
import cv2 as cv
import math
import datetime

# M = 1024
# N = 768

# img = np.zeros((N,M), dtype=np.uint8)

# cv.line(img, (0,0), (M-1, N-1), 255)

# cv.imshow('image', img )
# if cv.waitKey(0) == 27:
#     cv.destroyAllWindows()

#Sử dụng CV vẽ một đường tròn trùng tâm với tâm của ảnh, có bán kính là 100, màu trắng, độ dày 2 pixel.
# cv.circle(img,(M//2,N//2),300,255,15)

# cv.imshow('image',img)
# if cv.waitKey(0) == 27:
#     cv.destroyAllWindows()



# m = 1024
# n = 768
# c = 3 
# cl_img = np.zeros((n,m,3),dtype=np.uint8)
# cl_img[10:300,:,0] = 255
# cl_img[250:500,:,1] = 255
# cl_img[450:700,:,2] = 255
# cv.imshow('color image',cl_img)
# cv.waitKey(0)
# # cv.destroyAllWindows()

# chessboard = np.zeros((800,800,3),dtype=np.uint8)
# for i in range(8):
#     for j in range(8):
#         if (i+j) % 2 == 0:
#             cv.rectangle(chessboard,(j*100,i*100), ((j+1)*100,(i+1)*100),(128,0,128)-1)
#         else:
#             cv.rectangle(chessboard,(j*100,i*100), ((j+1)*100,(i+1)*100),(0,255,0)-1)
# cv.imshow('chessboard',chessboard)
# cv.waitKey(0)
# cv.destroyAllWindows()

#Vẽ mặt đồng hồ hình tròn, nền màu tím, có các số dạng la mã màu sắc khác nhau. 
#Có 3 kim đồng hồ: Giờ, phút, giây.
#Kim giờ màu xanh dương, kim phút màu xanh lá cây, kim giây màu đỏ.
#level 2: Vẽ kim giây chuyển động.
#level 3: Vẽ kim phút chuyển động.
#level 4: Vẽ kim giờ chuyển động.   
#level 5: Vẽ thêm các vạch chỉ phút trên mặt đồng hồ. Và kim giây, kim giờ, kim phút, hoạt động theo logic


# def draw_clock():
#     while True:
#         # Tạo nền tím (BGR: Purple = 128, 0, 128)
#         img = np.zeros((600, 600, 3), dtype=np.uint8)
#         img[:] = (128, 0, 128)
        
#         center = (300, 300)
#         radius = 250
        
#         # 1. Vẽ mặt đồng hồ trắng (Level 1)
#         cv2.circle(img, center, radius, (255, 255, 255), 3)

        # 2. Lấy thời gian thực & Tính góc (Level 5 logic)
        # now = datetime.datetime.now()
        # h, m, s = now.hour, now.minute, now.second

        # # Tính góc (đổi sang radian vì OpenCV dùng sin/cos)
        # # Trừ 90 độ (pi/2) vì trong toán học 0 độ nằm ở hướng 3 giờ
        # sec_angle = math.radians(s * 6 - 90)
        # min_angle = math.radians(m * 6 - 90)
        # hour_angle = math.radians((h % 12) * 30 + m * 0.5 - 90)

#         # 3. Vẽ kim đồng hồ (Level 1, 2, 3, 4)
#         # Kim Giờ - Xanh dương (BGR: 255, 0, 0)
#         cv2.line(img, center, (int(300 + 120 * math.cos(hour_angle)), int(300 + 120 * math.sin(hour_angle))), (255, 0, 0), 8)
#         # Kim Phút - Xanh lá (BGR: 0, 255, 0)
#         cv2.line(img, center, (int(300 + 170 * math.cos(min_angle)), int(300 + 170 * math.sin(min_angle))), (0, 255, 0), 5)
#         # Kim Giây - Đỏ (BGR: 0, 0, 255)
#         cv2.line(img, center, (int(300 + 200 * math.cos(sec_angle)), int(300 + 200 * math.sin(sec_angle))), (0, 0, 255), 2)

#         # 4. Vẽ số La Mã đơn giản (Level 1)
#         roman = ["XII", "III", "VI", "IX"]
#         pos = [(300, 80), (520, 310), (280, 540), (60, 310)]
#         for i in range(4):
#             cv2.putText(img, roman[i], pos[i], cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

#         # Hiển thị
#         cv2.imshow("Dong ho OpenCV", img)
        
#         # Nhấn 'q' để thoát
#         if cv2.waitKey(1000) & 0xFF == ord('q'):
#             break

#     cv2.destroyAllWindows()

# draw_clock()


import cv2 as cv
import numpy as np
import datetime
import math
def run_clock():
    while True:
        # 1. Tạo nền và vẽ mặt đồng hồ (Level 1)
        # Chúng ta tạo lại clock_face ở mỗi vòng lặp để xóa kim cũ
        clock_face = np.zeros((600, 600, 3), dtype=np.uint8)
        clock_face[:] = (128, 0, 128)  # Nền tím
        center = (300, 300)
        cv.circle(clock_face, center, 250, (255, 255, 255), 3)

        # 2. Vẽ các vạch chỉ phút (Level 5)
        for i in range(60):
            angle = math.radians(i * 6)
            p1 = (int(300 + 230 * math.cos(angle)), int(300 + 230 * math.sin(angle)))
            p2 = (int(300 + 245 * math.cos(angle)), int(300 + 245 * math.sin(angle)))
            cv.line(clock_face, p1, p2, (255, 255, 255), 1 if i % 5 != 0 else 3)

        # 3. Lấy thời gian thực & Tính góc (Level 2, 3, 4, 5)
        now = datetime.datetime.now()
        h, m, s = now.hour, now.minute, now.second

        sec_angle = math.radians(s * 6 - 90)
        min_angle = math.radians(m * 6 - 90)
        hour_angle = math.radians((h % 12) * 30 + m * 0.5 - 90)

        # 4. Vẽ số La Mã
        roman_numerals = ["XII", "III", "VI", "IX"]
        positions = [(275, 90), (510, 310), (280, 530), (70, 310)]
        for i in range(4):
            cv.putText(clock_face, roman_numerals[i], positions[i], cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # 5. Vẽ 3 kim chuyển động (Giờ: Xanh dương, Phút: Xanh lá, Giây: Đỏ)
        # Kim Giờ
        cv.line(clock_face, center, (int(300 + 120 * math.cos(hour_angle)), int(300 + 120 * math.sin(hour_angle))), (255, 0, 0), 8)
        # Kim Phút
        cv.line(clock_face, center, (int(300 + 170 * math.cos(min_angle)), int(300 + 170 * math.sin(min_angle))), (0, 255, 0), 5)
        # Kim Giây
        cv.line(clock_face, center, (int(300 + 200 * math.cos(sec_angle)), int(300 + 200 * math.sin(sec_angle))), (0, 0, 255), 2)

        # 6. Hiển thị lên màn hình
        cv.imshow("Dong ho tu dong", clock_face)

        # 7. Chờ 1 giây (1000ms) rồi lặp lại, nhấn 'q' để thoát
        if cv.waitKey(1000) & 0xFF == ord('q'):
            break

    cv.destroyAllWindows()

# Gọi hàm để chạy
run_clock()