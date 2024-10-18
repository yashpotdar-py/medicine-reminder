import sys
import os
# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import schedule
import threading
import streamlit as st
from backend.ocr import extract_text_from_image
from backend.reminders import text_to_speech_reminder
from database.db import init_auth_db, register_user, login_user, store_extracted_text, store_medicine_schedule, get_medicine_schedule
from backend.audio_to_text import convert_audio_to_text
from backend.pdf_to_text import convert_pdf_to_text
from backend.scheduler import schedule_medicine_reminder, run_scheduler


# Initialize the authentication database
init_auth_db()

# Check if the user is already logged in
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['user'] = None

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a Page:", ["Home", "Login", "Register", "Upload", "Reminders"])

# Home Page
if page == "Home":
    if not st.session_state['logged_in']:
        st.warning("You need to log in to access the home page.")
        page = "Login"  # Redirect to Login page if not logged in

    if st.session_state['logged_in']:
        st.title("Welcome to Medicine Reminder App!")
        st.write("This is your home page. Please use the features provided.")

        st.header("Add Medication Schedule")
        with st.form("medicine_form"):
            medicine_name = st.text_input("Enter the medicine name")
            morning_dose = st.checkbox("Morning")
            afternoon_dose = st.checkbox("Afternoon")
            night_dose = st.checkbox("Night")
            submitted = st.form_submit_button("Add Medicine")

        if submitted:
            # Store the medication schedule in the database
            if medicine_name:
                medicine_schedule = {
                    "medicine_name": medicine_name,
                    "morning": morning_dose,
                    "afternoon": afternoon_dose,
                    "night": night_dose
                }
                # Store the schedule in the database
                store_medicine_schedule(st.session_state['user'], medicine_schedule)

                # Schedule reminders for the medicine
                schedule_medicine_reminder(medicine_schedule, st.session_state['user'])

                st.success(f"Medicine '{medicine_name}' schedule added successfully with reminders!")
            else:
                st.error("Please enter a valid medicine name.")

        # Display current medication schedule (if any)
        st.header("Your Medication Schedule")
        schedule = get_medicine_schedule(st.session_state['user'])

        if schedule:
            for item in schedule:
                st.write(f"**Medicine**: {item['medicine_name']}")
                st.write(f"Morning: {'Yes' if item['morning'] else 'No'}")
                st.write(f"Afternoon: {'Yes' if item['afternoon'] else 'No'}")
                st.write(f"Night: {'Yes' if item['night'] else 'No'}")
                st.write("---")
        else:
            st.write("No medication schedule found. Add your medication above.")

# Login Page
elif page == "Login":
    st.header("User Login")
    login_username = st.text_input("Username", key="login_username")
    login_password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        user = login_user(login_username, login_password)

        if user:
            st.session_state['logged_in'] = True
            st.session_state['user'] = user[1]  # Store the username in the session
            st.success(f"Welcome {login_username}!")
            page = "Home"  # Redirect to Home page
        else:
            st.error("Invalid username or password")

# Registration Page
elif page == "Register":
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

# Upload Page
elif page == "Upload":
    if not st.session_state['logged_in']:
        st.warning("You need to log in to access this page.")
        page = "Login"
    else:
        st.header("Upload Audio or PDF")
        uploaded_file = st.file_uploader("Choose an audio file (WAV, MP3) or PDF file", type=["wav", "mp3", "pdf"])

        if uploaded_file is not None:
            if uploaded_file.type in ["audio/wav", "audio/mp3"]:
                # Convert audio to text
                text = convert_audio_to_text(uploaded_file)
                if text:
                    st.success("Audio converted to text successfully!")
                    st.text_area("Extracted Text", text, height=300)
                    if st.button("Store Extracted Text"):
                        store_extracted_text(st.session_state['user'], text)
                        st.success("Text stored successfully!")
                else:
                    st.error("Failed to convert audio to text.")

            elif uploaded_file.type == "application/pdf":
                # Convert PDF to text
                text = convert_pdf_to_text(uploaded_file)
                if text:
                    st.success("PDF converted to text successfully!")
                    st.text_area("Extracted Text", text, height=300)
                    if st.button("Store Extracted Text"):
                        store_extracted_text(st.session_state['user'], text)
                        st.success("Text stored successfully!")
                else:
                    st.error("Failed to convert PDF to text.")

# Reminders Page
elif page == "Reminders":
    st.header("Your Scheduled Reminders")
    if st.session_state['logged_in']:
        try:
            jobs = schedule.get_jobs()
            if jobs:
                for job in jobs:
                    reminder_message = job.job_func.args[0]  # Assuming first arg is the reminder message
                    next_run_time = job.next_run.strftime('%H:%M')  # Get next run time
                    st.write(f"Reminder: {reminder_message} at {next_run_time}")
            else:
                st.write("No reminders have been scheduled.")
        except Exception as e:
            st.error(f"Error fetching scheduled jobs: {e}")
    else:
        st.warning("You need to log in to access this page.")

# Start the reminder scheduler in a separate thread
if not st.session_state.get('scheduler_running'):
    st.session_state['scheduler_running'] = True
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
