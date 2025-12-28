import cv2
import mediapipe as mp
import random
import time

# Mediapipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Webcam (IMPORTANT for Windows)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

options = ["Rock", "Paper", "Scissors"]

def get_gesture(finger_tips):
    if finger_tips == [0, 0, 0, 0, 0]:
        return "Rock"
    elif finger_tips == [1, 1, 1, 1, 1]:
        return "Paper"
    elif finger_tips == [0, 1, 1, 0, 0]:
        return "Scissors"
    return None

def count_fingers(hand_landmarks):
    tips_ids = [4, 8, 12, 16, 20]
    fingers = []

    # Thumb
    fingers.append(
        1 if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x else 0
    )

    # Other fingers
    for i in range(1, 5):
        fingers.append(
            1 if hand_landmarks.landmark[tips_ids[i]].y <
            hand_landmarks.landmark[tips_ids[i]-2].y else 0
        )
    return fingers

# Game state
countdown_start = time.time()
countdown_time = 3
state = "COUNTDOWN"

player_choice = ""
computer_choice = ""
winner = ""

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if state == "COUNTDOWN":
        elapsed = int(time.time() - countdown_start)
        remaining = countdown_time - elapsed

        if remaining > 0:
            cv2.putText(frame, f"Get Ready: {remaining}",
                        (150, 200), cv2.FONT_HERSHEY_SIMPLEX,
                        2, (0, 255, 255), 4)
        else:
            state = "PLAY"
            player_choice = ""

    elif state == "PLAY":
        cv2.putText(frame, "GO!",
                    (250, 200), cv2.FONT_HERSHEY_SIMPLEX,
                    2.5, (0, 255, 0), 5)

        if result.multi_hand_landmarks:
            hand_landmarks = result.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            fingers = count_fingers(hand_landmarks)
            gesture = get_gesture(fingers)

            if gesture:
                player_choice = gesture
                computer_choice = random.choice(options)

                if player_choice == computer_choice:
                    winner = "Tie"
                elif (player_choice == "Rock" and computer_choice == "Scissors") or \
                     (player_choice == "Paper" and computer_choice == "Rock") or \
                     (player_choice == "Scissors" and computer_choice == "Paper"):
                    winner = "You Win!"
                else:
                    winner = "Computer Wins!"

                state = "RESULT"
                result_time = time.time()

    elif state == "RESULT":
        if time.time() - result_time > 2:
            state = "COUNTDOWN"
            countdown_start = time.time()

    # Display results
    cv2.putText(frame, f"You: {player_choice}", (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f"Computer: {computer_choice}", (10, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(frame, f"Winner: {winner}", (10, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    cv2.imshow("Rock Paper Scissors", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
