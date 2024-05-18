import cv2
import numpy as np
from random import choice

REV_CLASS_MAP = {
    0: "rock",
    1: "paper",
    2: "scissors",
    3: "none"
}

def mapper(val):
    return REV_CLASS_MAP[val]

def calculate_winner(move1, move2):
    if move1 == move2:
        return "Tie"

    if move1 == "rock":
        if move2 == "scissors":
            return "User"
        if move2 == "paper":
            return "Computer"

    if move1 == "paper":
        if move2 == "rock":
            return "User"
        if move2 == "scissors":
            return "Computer"

    if move1 == "scissors":
        if move2 == "paper":
            return "User"
        if move2 == "rock":
            return "Computer"

# 프레임의 너비와 높이 설정
frame_width = 1200
frame_height = 600

# VideoCapture 객체 생성
cap = cv2.VideoCapture(0)

# VideoCapture 객체의 속성 설정
cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

# Define icon size
ICON_WIDTH = 200
ICON_HEIGHT = 200

# Computer의 움직임 무작위 생성
computer_move_name = choice(['rock', 'paper', 'scissors'])

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    # rectangle for user to play
    cv2.rectangle(frame, (100, 100), (500, 500), (255, 255, 255), 2)
    # rectangle for computer to play
    cv2.rectangle(frame, (700, 100), (1100, 500), (255, 255, 255), 2)

    # 아이콘 표시
    icon = cv2.imread(f"images/{computer_move_name}.png")
    icon = cv2.resize(icon, (ICON_WIDTH, ICON_HEIGHT))
    frame[100:100+ICON_HEIGHT, 700:700+ICON_WIDTH] = icon

    # 사용자의 움직임 생성
    move_code_user = np.random.randint(0, 3)
    user_move_name = mapper(move_code_user)

    # 예측한 사용자의 움직임과 컴퓨터의 움직임을 화면에 표시
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frame, "Your Move: " + user_move_name,
                (50, 50), font, 1.2, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, "Computer's Move: " + computer_move_name,
                (700, 50), font, 1.2, (255, 255, 255), 2, cv2.LINE_AA)

    # 이긴 플레이어 표시
    winner = calculate_winner(user_move_name, computer_move_name)
    cv2.putText(frame, "Winner: " + winner,
                (400, 600), font, 2, (0, 0, 255), 4, cv2.LINE_AA)

    # 화면에 프레임 출력
    cv2.imshow("Rock Paper Scissors", frame)

    # 'q'를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# VideoCapture 객체 해제
cap.release()

# 모든 창 닫기
cv2.destroyAllWindows()
