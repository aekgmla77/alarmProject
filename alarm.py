import cv2
import numpy as np
from datetime import datetime

# 시간과 분 입력 받기
hour = int(input('시를 입력하세요 (0-23): '))
minute = int(input('분을 입력하세요 (0-59): '))

target_time = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)


cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 현재 시간 가져오기
    now = datetime.now()

    # 손 모양을 검출하기 위해 피부색 범위 지정
    lower_skin = np.array([0, 48, 80], dtype=np.uint8)
    upper_skin = np.array([20, 255, 255], dtype=np.uint8)

    # 이미지를 HSV 색 공간으로 변환
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 지정한 피부색 범위 내의 픽셀만 추출
    mask = cv2.inRange(hsv, lower_skin, upper_skin)

    # 노이즈 제거를 위해 모폴로지 연산 적용
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # 손 모양의 윤곽을 찾기 위해 외곽선 검출
    contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 윤곽선을 따라 손 모양 그리기
    if len(contours) > 0:
        max_contour = max(contours, key=cv2.contourArea)
        cv2.drawContours(frame, [max_contour], -1, (0, 255, 0), 2)

    cv2.imshow('Hand Detection', frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()