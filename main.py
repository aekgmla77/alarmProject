import cv2
import numpy as np
from tensorflow.keras.models import load_model
from random import choice
from datetime import datetime, timedelta
import time
import pygame
import tkinter as tk
from PIL import Image, ImageTk

# 클래스 매핑 딕셔너리
REV_CLASS_MAP = {
    0: "paper",
    1: "rock",
    2: "scissors",
    3: "none"
}

def mapper(val):
    return REV_CLASS_MAP[val]

# 이긴 플레이어 결정 함수
def calculate_winner(move1, move2):
    if move1 == move2:
        return "tie"
    if move1 == "rock" and move2 == "scissors":
        return "user"
    if move1 == "paper" and move2 == "rock":
        return "user"
    if move1 == "scissors" and move2 == "paper":
        return "user"
    return "computer"

# 손 모양 인식 함수
def detect_hand(model, frame):
    img = cv2.resize(frame, (224, 224))
    img = np.array(img, dtype=np.float32)
    img = np.expand_dims(img, axis=0)
    img = img / 255.0  # 이미지 스케일링
    pred = model.predict(img)
    move_code = np.argmax(pred[0])
    confidence = np.max(pred[0])  # 최대 예측 확률

    # 예측 확률이 0.75 이상일 때만 손 모양 인식
    if confidence < 0.75:
        return "none"
    else:
        return REV_CLASS_MAP[move_code]

# 게임 시작 시간 설정
def set_game_start_time():
    start_hour = int(input("게임을 시작할 시간을 시간 단위로 입력하세요 (예: 1): "))
    start_minute = int(input("게임을 시작할 시간을 분 단위로 입력하세요 (예: 30): "))
    current_time = datetime.now()
    start_time = current_time.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
    if start_time < current_time:
        start_time += timedelta(days=1)
    print(f"게임이 {start_time.strftime('%H:%M:%S')}에 시작됩니다.")
    return start_time

# 알람 소리 재생 함수
def play_alarm_sound(file_path, loop=False):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play(loops=-1 if loop else 0)  # 무한 반복 재생

# 알람 소리 정지 함수
def stop_alarm_sound():
    pygame.mixer.music.stop()

# 모델 로드
print("모델을 로드하는 중...")
try:
    model = load_model("rock-paper-scissors-model.keras")
    print("모델 로드 완료")
except Exception as e:
    print(f"모델을 로드할 수 없습니다: {e}")
    exit()

start_time = set_game_start_time()

# 게임 시작 시간까지 대기
while datetime.now() < start_time:
    time.sleep(1)

# 알람 소리 재생
play_alarm_sound(r'C:\Users\LG\Downloads\Oasis - Dont Look Back In Anger (Official Video).mp3', loop=True)

# Tkinter 창 생성
root = tk.Tk()
root.title("Rock Paper Scissors")
root.geometry("1200x600")

# Tkinter 캔버스 생성
canvas = tk.Canvas(root, width=1500, height=1200)
canvas.pack()

# VideoCapture 객체 생성 및 설정
print("비디오 캡처 객체를 생성하는 중...")
# 여러 카메라 디바이스 번호 시도
for i in range(10):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"카메라 {i}번 장치 사용 중")
        break
else:
    print("사용 가능한 카메라를 찾을 수 없습니다.")
    exit()

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1300)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 800)
print("비디오 캡처 객체 생성 완료")

# 카메라가 안정적으로 동작하도록 대기
time.sleep(2)

# Define icon size
ICON_WIDTH = 400
ICON_HEIGHT = 400

# 컴퓨터의 움직임 무작위 생성
computer_move_name = choice(['rock', 'paper', 'scissors'])

frame_counter = 0
user_move_name = "none"
start_recognition_time = datetime.now() + timedelta(seconds=5)  # 인식 시작 시간 조정

# 이는 사용자 경험이 향상될 수 있도록 합니다.
def update_frame():
    global frame_counter, user_move_name
    ret, frame = cap.read()
    if not ret:
        print("프레임을 읽어오지 못했습니다.")
        root.after(1000, update_frame)  # 업데이트 주기 변경
        return

    # 사용자와 컴퓨터 영역에 사각형 표시
    cv2.rectangle(frame, (100, 100), (500, 500), (255, 255, 255), 2)
    cv2.rectangle(frame, (700, 100), (1100, 500), (255, 255, 255), 2)

    # 컴퓨터의 아이콘 표시
    icon = cv2.imread(f"images/{computer_move_name}.png")
    if icon is not None:
        icon = cv2.resize(icon, (ICON_WIDTH, ICON_HEIGHT))
        frame[100:100+ICON_HEIGHT, 700:700+ICON_WIDTH] = icon

    # 손 영역 자르기 및 사용자 손 모양 인식 (프레임 카운터를 사용하여 인식 주기를 조절)
    if frame_counter % 10 == 0 and datetime.now() >= start_recognition_time:  # 매 10 프레임마다 한 번씩 손 모양 인식, 일정 시간 후 인식 시작
        hand_area = frame[100:500, 100:500]
        new_user_move_name = detect_hand(model, hand_area)
        if new_user_move_name != "none":
            user_move_name = new_user_move_name
            print(f"인식된 사용자의 움직임: {user_move_name}")

    # 사용자와 컴퓨터의 움직임, 이긴 플레이어 표시
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frame, "Your Move: " + user_move_name, (50, 50), font, 1.2, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, "Computer's Move: " + computer_move_name, (700, 50), font, 1.2, (255, 255, 255), 2, cv2.LINE_AA)

    if user_move_name != "none":
        winner = calculate_winner(user_move_name, computer_move_name)
        cv2.putText(frame, "Winner: " + winner, (400, 550), font, 2, (0, 0, 255), 4, cv2.LINE_AA)
        if winner == "user":
            print("사용자가 이겼습니다. 게임을 종료합니다.")
            stop_alarm_sound()
            time.sleep(2)
            root.destroy()
            return
    else:
        print("손 모양 인식 실패. 다시 시도 중...")

    # OpenCV 이미지를 Tkinter에서 사용 가능한 이미지 형식으로 변환
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    imgtk = ImageTk.PhotoImage(image=img)

    # 캔버스에 이미지 업데이트
    canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
    canvas.imgtk = imgtk

    frame_counter += 1
    root.after(100, update_frame)  # 업데이트 주기 변경

# 게임의 메인 루프 실행
root.after(0, update_frame)
root.mainloop()

cap.release()
cv2.destroyAllWindows()
print("게임 종료")
