import sys
import os

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db import init_auth_db, register_user, login_user
from backend.reminders import text_to_speech_reminder
from backend.ocr import extract_text_from_image
import streamlit as st

# Initialize the authentication database
init_auth_db()

# Check if the user is already logged in
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['user'] = None

# User Registration
if not st.session_state['logged_in']:
    st.header("User Registration")
    username = st.text_input("Enter a username")
    password = st.text_input("Enter a password", type="password")
    confirm_password = st.text_input("Confirm password", type="password")

    if st.button("Register"):
        if password != confirm_password:
            st.error("Passwords do not match!")
        elif register_user(username, password):
            st.success(f"User {username} registered successfully!")
        else:
            st.error("Username already exists!")

# User Login
st.header("User Login")
login_username = st.text_input("Username", key="login_username")
login_password = st.text_input(
    "Password", type="password", key="login_password")

if st.button("Login"):
    user = login_user(login_username, login_password)

    if user:
        st.session_state['logged_in'] = True
        st.session_state['user'] = user[1]  # Store the username in the session
        st.success(f"Welcome {login_username}!")
    else:
        st.error("Invalid username or password")

# Check login state and show logged-in content
if st.session_state['logged_in']:
    st.write(f"Logged in as {st.session_state['user']}")

    # Logout button
    if st.button("Logout"):
        st.session_state['logged_in'] = False
        st.session_state['user'] = None
        st.success("Logged out successfully!")

    # Prescription upload and OCR
    st.header("Upload Prescription")
    uploaded_file = st.file_uploader(
        "Upload your prescription (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Prescription",
                 use_column_width=True)
        extracted_text = extract_text_from_image(uploaded_file)
        if extracted_text:
            st.text_area("Extracted Prescription Text", extracted_text)

            # You can further add parsing and scheduling logic here
else:
    st.write("Please log in to access the app.")
