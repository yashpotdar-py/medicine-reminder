import sys
import os

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from backend.ocr import extract_text_from_image
from database.db import init_db, add_user, get_users
from backend.scheduler import schedule_reminder
from backend.remiders import text_to_speech_reminder

# Initialize the database
init_db()

st.title("Voice-Enabled Medicine Reminder")

# User selection or registration
st.header("User Profile")
users = get_users()
user_names = [user[1] for user in users]
selected_user = st.selectbox("Select a user", user_names)

# Add new user
new_user = st.text_input("Add new user")
if st.button("Add User"):
    add_user(new_user)
    st.success(f"User {new_user} added successfully!")

# Upload prescription
st.header("Prescription Upload")
uploaded_file = st.file_uploader("Choose an image", type=["png", "jpg", "jpeg"])
if uploaded_file is not None:
    text = extract_text_from_image(uploaded_file)
    st.text_area("Extracted Text", text)

# Schedule reminders
st.header("Schedule Reminder")
medicine_name = st.text_input("Medicine Name")
dosage = st.text_input("Dosage")
reminder_time = st.time_input("Reminder Time")
if st.button("Set Reminder"):
    from datetime import datetime
    reminder_datetime = datetime.combine(datetime.today(), reminder_time)
    
    schedule_reminder(1, reminder_datetime, medicine_name, dosage)  # Hardcoded user ID for simplicity
    text_to_speech_reminder(medicine_name, dosage)
    st.success("Reminder set successfully!")
