import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import os
import speech_recognition as sr
import pyautogui
import time

st.set_page_config(page_title="🖐️ Gesture-Controlled Desktop Controller", layout="centered")
st.title("🖐️ Voice & Finger-Controlled Desktop Controller")

# Session state for camera on/off
if 'camera_on' not in st.session_state:
    st.session_state.camera_on = False

FRAME_WINDOW = st.image([])
captured_image = st.empty()

# MediaPipe hands setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

def count_fingers(hand_landmarks):
    finger_tips = [8, 12, 16, 20]
    count = 0
    # Thumb
    if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
        count += 1
    # Other fingers
    for tip in finger_tips:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            count += 1
    return count

def listen_for_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Say 'open camera' to activate webcam...")
        try:
            audio = r.listen(source, timeout=5)
            command = r.recognize_google(audio).lower()
            return command
        except (sr.UnknownValueError, sr.WaitTimeoutError):
            return ""

def perform_action(fingers, frame):
    if fingers == 1:
        st.info("🔉 Volume Down")
        pyautogui.press("volumedown")
    elif fingers == 2:
        st.info("🔊 Volume Up")
        pyautogui.press("volumeup")
    elif fingers == 3:
        st.info("⏹️ Media Stop")
        pyautogui.press("playpause")
        pyautogui.press("playpause")
    elif fingers == 4:
        st.info("🌐 Opening Chrome...")
        os.system("start chrome")
        return True
    elif fingers == 5:
        photo_path = "photo_5_fingers.png"
        cv2.imwrite(photo_path, frame)
        st.success("📸 Photo captured!")
        captured_image.image(photo_path, caption="Captured (5 fingers)")
        st.info("📝 Opening Notepad...")
        os.system("start notepad")
        return True
    elif fingers == 10:
        st.warning("🕐 10 fingers detected. Capturing photo in 5 seconds...")
        FRAME_WINDOW.image(frame, channels='BGR')
        time.sleep(5)
        photo_path = "photo_10_fingers.png"
        cv2.imwrite(photo_path, frame)
        st.success("📸 Photo captured after 5 sec (10 fingers)")
        captured_image.image(photo_path, caption="Captured (10 fingers)")
        return False
    return False

# Voice command button
if st.button("🎧 Start Voice Listener"):
    command = listen_for_command()
    st.write(f"Recognized: `{command}`")
    if "open camera" in command:
        st.session_state.camera_on = True
        st.success("✅ Camera activated!")

# Main camera loop
if st.session_state.camera_on:
    cap = cv2.VideoCapture(0)
    last_action_time = 0
    cooldown = 1  # seconds cooldown between actions

    while True:
        ret, frame = cap.read()
        if not ret:
            st.error("Webcam error.")
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                fingers = count_fingers(hand_landmarks)

                cv2.putText(frame, f'Fingers: {fingers}', (10, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                current_time = time.time()
                if current_time - last_action_time > cooldown:
                    action_result = perform_action(fingers, frame)
                    if action_result:
                        cap.release()
                        st.session_state.camera_on = False
                        st.stop()
                    last_action_time = current_time

        FRAME_WINDOW.image(frame, channels='BGR')

    cap.release()
