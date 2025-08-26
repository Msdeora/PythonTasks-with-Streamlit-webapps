# All-in-One Python Utility Dashboard (Streamlit)

import streamlit as st
import subprocess
import pywhatkit
from twilio.rest import Client as TwilioClient
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime
import requests
from instagrapi import Client as InstaClient
import qrcode
import io
import random
import socket
import platform
import cv2
from PIL import Image
import numpy as np
import webbrowser
import paramiko

# PAGE SETTINGS
st.set_page_config(page_title="🧰 Python MultiTool Dashboard", layout="wide")
st.title("🧰 All-in-One Python Utility Dashboard")

# MAIN MENU
tool = st.sidebar.selectbox("🔍 Select Tool", [
    "🔐 SSH Remote Commands",
    "💬 WhatsApp Messaging",
    "📞 Twilio Call & SMS",
    "🔍 Google Search",
    "📧 Send Gmail",
    "🌭 Email Spoofing (Educational)",
    "📸 Instagram Post",
    "🧠 Bonus: QR & Weather",
    "🧪 System Info & Password Generator",
    "📷 Camera Snapshot"
])

########################################
# 1. SSH Remote Commands
########################################
if tool == "🔐 SSH Remote Commands":
    st.subheader("🔐 SSH Remote Command Executor")
    host = st.text_input("Host (IP or domain)")
    port = st.number_input("Port", value=22)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    command = st.text_area("Enter Linux command to run")

    if st.button("Execute SSH Command"):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, port, username, password, timeout=5)
            stdin, stdout, stderr = ssh.exec_command(command)
            output = stdout.read().decode()
            error = stderr.read().decode()
            ssh.close()
            st.success("✅ Command Executed!")
            st.code(output or error)
        except Exception as e:
            st.error(f"❌ SSH Error: {e}")

########################################
# 2. WhatsApp Messaging
########################################
elif tool == "💬 WhatsApp Messaging":
    st.subheader("💬 Send WhatsApp Message")
    number = st.text_input("Enter phone number (with +91 etc.)")
    message = st.text_area("Message to send")
    hour = st.number_input("Hour (24h)", 0, 23, value=datetime.datetime.now().hour)
    minute = st.number_input("Minute", 0, 59, value=(datetime.datetime.now().minute + 2) % 60)
    if st.button("Send Message"):
        try:
            pywhatkit.sendwhatmsg(number, message, hour, minute)
            st.success("✅ Message scheduled successfully!")
        except Exception as e:
            st.error(f"Error: {e}")

########################################
# 3. Twilio Call & SMS
########################################
elif tool == "📞 Twilio Call & SMS":
    st.subheader("📞 Twilio Call & SMS Sender")
    acc_sid = st.text_input("Twilio Account SID")
    auth_token = st.text_input("Twilio Auth Token", type="password")
    from_no = st.text_input("Twilio Phone Number")
    to_no = st.text_input("Recipient Phone Number")
    action = st.radio("Action", ["Send SMS", "Make Call"])
    message = st.text_area("Message")

    if st.button("Execute Twilio Action"):
        try:
            client = TwilioClient(acc_sid, auth_token)
            if action == "Send SMS":
                client.messages.create(body=message, from_=from_no, to=to_no)
                st.success("✅ SMS Sent!")
            else:
                call = client.calls.create(
                    twiml=f'<Response><Say>{message}</Say></Response>',
                    to=to_no,
                    from_=from_no
                )
                st.success(f"✅ Call initiated: {call.sid}")
        except Exception as e:
            st.error(f"❌ Error: {e}")

########################################
# 4. Google Search
########################################
elif tool == "🔍 Google Search":
    st.subheader("🔍 Google Search via Python")
    query = st.text_input("Search Term")
    if st.button("Search"):
        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)
        st.success("✅ Search opened in your browser.")

########################################
# 5. Send Gmail
########################################
elif tool == "📧 Send Gmail":
    st.subheader("📧 Send Email via Gmail SMTP")
    sender = st.text_input("Your Gmail")
    pwd = st.text_input("App Password", type="password")
    receiver = st.text_input("Receiver Email")
    subject = st.text_input("Subject")
    body = st.text_area("Message")

    if st.button("Send Email"):
        try:
            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = receiver
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender, pwd)
            server.send_message(msg)
            server.quit()
            st.success("✅ Email sent successfully.")
        except Exception as e:
            st.error(f"❌ Error: {e}")

########################################
# 6. Email Spoofing (Educational)
########################################
elif tool == "🌭 Email Spoofing (Educational)":
    st.subheader("🌭 Educational Email Spoofing (Offline Demo)")
    fake_from = st.text_input("Fake From")
    to = st.text_input("To")
    subject = st.text_input("Subject")
    msg = st.text_area("Message Body")
    if st.button("Generate Spoof Email (Simulation)"):
        spoof = f"From: {fake_from}\nTo: {to}\nSubject: {subject}\n\n{msg}"
        st.code(spoof)

########################################
# 7. Instagram Post
########################################
elif tool == "📸 Instagram Post":
    st.subheader("📸 Upload Instagram Image via `instagrapi`")
    insta_user = st.text_input("Instagram Username")
    insta_pass = st.text_input("Instagram Password", type="password")
    img_file = st.file_uploader("Upload image", type=["jpg", "png"])
    caption = st.text_area("Caption")
    if st.button("Post to Instagram"):
        try:
            cl = InstaClient()
            cl.login(insta_user, insta_pass)
            with open("temp.jpg", "wb") as f:
                f.write(img_file.read())
            cl.photo_upload("temp.jpg", caption)
            st.success("✅ Posted to Instagram!")
        except Exception as e:
            st.error(f"❌ Error: {e}")

########################################
# 8. Bonus: QR & Weather
########################################
elif tool == "🧠 Bonus: QR & Weather":
    st.subheader("🎯 Bonus Tools")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🔳 QR Code Generator")
        qr_text = st.text_input("Text to encode in QR")
        if st.button("Generate QR"):
            img = qrcode.make(qr_text)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            st.image(buf.getvalue(), caption="🔳 QR Code")
            st.download_button("Download QR", buf.getvalue(), "qr.png")

    with col2:
        st.markdown("### ☁️ Weather Checker")
        city = st.text_input("City name")
        if st.button("Check Weather"):
            try:
                res = requests.get(f"https://wttr.in/{city}?format=3")
                st.success(res.text)
            except Exception as e:
                st.error(f"❌ {e}")

########################################
# 9. System Info & Password Generator
########################################
elif tool == "🧪 System Info & Password Generator":
    st.subheader("🧪 System Info")
    st.code(f"OS: {platform.system()} {platform.release()}")
    st.code(f"Python Version: {platform.python_version()}")
    st.code(f"Host: {socket.gethostname()}")
    st.code(f"IP Address: {socket.gethostbyname(socket.gethostname())}")

    st.subheader("🔑 Random Password Generator")
    length = st.slider("Password Length", 4, 32, value=12)
    if st.button("Generate Password"):
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()"
        password = "".join(random.choices(chars, k=length))
        st.code(password)

########################################
# 10. Camera Snapshot + Digital Image Creator
########################################
elif tool == "📷 Camera Snapshot":
    st.subheader("📷 Take a Photo from Webcam")

    if st.button("Capture Image"):
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()

        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(frame_rgb)
            st.image(img_pil, caption="📸 Captured Image")

            buf = io.BytesIO()
            img_pil.save(buf, format="PNG")
            st.download_button("📥 Download Image", data=buf.getvalue(), file_name="captured_image.png", mime="image/png")

            arr = np.array(img_pil)
            st.subheader("🧮 Image Details")
            st.text(f"Image Shape: {arr.shape}")
            st.text(f"Example Pixel at [0,0]: {arr[0,0]}")
            st.text(f"Total Pixels: {arr.shape[0] * arr.shape[1]}")
            st.text("Bits per pixel: 24 (8 bits per RGB channel)")

            gray = np.mean(arr, axis=2).astype(np.uint8)
            st.subheader("🌎 Grayscale Pixel Matrix")
            st.dataframe(gray)
        else:
            st.error("❌ Could not capture image from webcam.")

    st.subheader("📤 Upload an Image")
    uploaded_file = st.file_uploader("Upload JPG or PNG", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="🖼️ Uploaded Image")

        np_data = np.array(image)
        st.subheader("🧮 Uploaded Image Details")
        st.text(f"Image Shape: {np_data.shape}")
        st.text(f"Example Pixel at [0,0]: {np_data[0,0]}")
        st.text(f"Total Pixels: {np_data.shape[0] * np_data.shape[1]}")
        st.text("Bits per pixel: 24 (8 bits per RGB channel)")

        gray_up = np.mean(np_data, axis=2).astype(np.uint8)
        st.subheader("🌎 Grayscale Pixel Matrix (Uploaded)")
        st.dataframe(gray_up)
