import sys
import pandas as pd
import plotly.express as px
import os
import streamlit as st
from datetime import datetime
from db import init_auth_db, register_user, login_user, store_medicine_schedule, get_medicine_schedule, store_reminder, get_reminders, delete_medicine_schedule, delete_reminder, update_medicine_schedule, update_reminder

from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
import datetime
import pyttsx3
import time
from dotenv import load_dotenv
import speech_recognition as sr
load_dotenv()
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = os.environ("GOOGLE_API_KEY")

engine = pyttsx3.init()

# Initialize the recognizer
r = sr.Recognizer()


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def check_medicine_time(vectorstore):
    current_time = datetime.datetime.now().strftime("%I:%M %p")

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0,
        max_output_tokens=2048,
    )

    retriever = vectorstore.as_retriever()

    prompt = ChatPromptTemplate.from_template("""
    Check if any medicine needs to be taken at {current_time}.
    If yes, create a reminder message. If no, respond with "No medicines scheduled for now."
    
    Context: {context}
    """)

    chain = (
        {"context": retriever | format_docs, "current_time": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain.invoke(current_time)


# Initialize the authentication database
init_auth_db()

# Check if the user is already logged in
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['user'] = None

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select a Page:", ["Home", "Login", "Register", "Schedule & Reminders", 'Upload', 'Voice Recognition'])

# Home Page
if page == "Home":
    st.title("Welcome to Your Medicine Reminder App! 💊")

    # Project Overview
    st.subheader("Project Overview")
    st.write("""
        The **Medicine Reminder App** is designed to help individuals manage their medication schedules effectively. 
        It provides a simple and intuitive interface to keep track of medications, set reminders, and ensure that 
        users never miss a dose.
    """)

    # Key Features Section
    st.subheader("Key Features")
    st.markdown("""
        - **User-Friendly Interface**: Easy navigation and a straightforward design to make medication management hassle-free.
        - **Medication Schedule**: Add, edit, and delete your medication schedules effortlessly.
        - **Reminders**: Set reminders for each medication to ensure timely intake.
        - **Prescription Upload**: Upload prescription PDFs for easy reference.
        - **Overview Dashboard**: Get insights into your medication habits and see your scheduled medicines visually represented.
    """)

    # Benefits Section
    st.subheader("Benefits of Using This App")
    st.markdown("""
        - **Stay Organized**: Keep all your medication schedules in one place.
        - **Improve Compliance**: Reduce the risk of missing doses by setting reminders.
        - **User Engagement**: The app provides an interactive experience that encourages regular use.
        - **Health Monitoring**: By tracking your medication intake, you can better manage your health conditions.
    """)

    # Add summary metrics (example values for demo purposes)
    st.subheader("Quick Overview")
    num_medicines = 0  # Placeholder for number of medicines
    num_reminders = 0   # Placeholder for number of reminders

    # Display some key metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Medicines", num_medicines, "medications added")
    with col2:
        st.metric("Active Reminders", num_reminders, "reminders set")

    # Add graphs (Example: Time of Day Medicine Schedule)
    st.subheader("Medication Schedule Overview")

    # For demo purposes, let's assume there's some sample schedule data
    sample_schedule_data = [
        {'medicine_name': 'Aspirin', 'morning': True, 'afternoon': False, 'night': True},
        {'medicine_name': 'Ibuprofen', 'morning': False, 'afternoon': True, 'night': False},
        {'medicine_name': 'Vitamin C', 'morning': True, 'afternoon': False, 'night': False},
    ]

    if sample_schedule_data:
        # Prepare data for graphing
        data = {
            'Medicine': [],
            'Time': []
        }

        for item in sample_schedule_data:
            if item['morning']:
                data['Medicine'].append(item['medicine_name'])
                data['Time'].append('Morning')
            if item['afternoon']:
                data['Medicine'].append(item['medicine_name'])
                data['Time'].append('Afternoon')
            if item['night']:
                data['Medicine'].append(item['medicine_name'])
                data['Time'].append('Night')

        df = pd.DataFrame(data)

        # Plot graph using Plotly
        fig = px.histogram(df, x="Time", color="Medicine", barmode="group",
                           title="Scheduled Medicines Throughout the Day",
                           labels={"Time": "Time of Day", "Medicine": "Medicine Name"},
                           category_orders={"Time": ["Morning", "Afternoon", "Night"]})
        st.plotly_chart(fig)

    else:
        st.info("No medication schedule available yet. Add some medications to see insights.")

    # Interactive buttons to explore scheduling features
    st.write("**Explore the features below:**")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Add a New Medicine 💊"):
            st.write("Feature coming soon! (Simulating adding medicine...)")

    with col2:
        if st.button("Set New Reminder ⏰"):
            st.write("Feature coming soon! (Simulating setting a reminder...)")

    with col3:
        if st.button("Upload Prescription PDF 📄"):
            st.write("Feature coming soon! (Simulating PDF upload...)")

    # Add an interactive slider for demo (e.g., tracking dosage frequency)
    st.subheader("Set Custom Dosage Frequency")
    dosage_frequency = st.slider(
        "How frequently do you take your medications? (Times per day)", min_value=1, max_value=5, value=3)
    st.write(f"You have set your dosage frequency to: {dosage_frequency} times per day.")

    st.write("Explore the app and take charge of your health!")

# Login Page
elif page == "Login":
    st.header("User Login")
    login_username = st.text_input("Username", key="login_username")
    login_password = st.text_input(
        "Password", type="password", key="login_password")

    if st.button("Login"):
        user = login_user(login_username, login_password)

        if user:
            st.session_state['logged_in'] = True
            st.session_state['user'] = user[1]
            st.success(f"Welcome {login_username}!")
            page = "Home"
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

elif page == "Schedule & Reminders":
    st.header("Manage Medication Schedule and Reminders")

    # Add Medication Schedule
    st.subheader("Add Medication Schedule")
    with st.form("medicine_form"):  # Unique form
        medicine_name = st.text_input("Enter the medicine name")
        morning_dose = st.checkbox("Morning")
        afternoon_dose = st.checkbox("Afternoon")
        night_dose = st.checkbox("Night")
        submitted = st.form_submit_button("Add Medicine")  # Submit button inside form

    if submitted:
        if medicine_name:
            medicine_schedule = {
                "medicine_name": medicine_name,
                "morning": morning_dose,
                "afternoon": afternoon_dose,
                "night": night_dose
            }
            store_medicine_schedule(st.session_state['user'], medicine_schedule)
            st.success(f"Medicine '{medicine_name}' schedule added successfully!")
        else:
            st.error("Please enter a valid medicine name.")

    # Display current medication schedule
    st.subheader("Your Medication Schedule")
    schedule = get_medicine_schedule(st.session_state['user'])

    if schedule:
        for item in schedule:
            with st.expander(f"Medicine: {item['medicine_name']}", expanded=False):
                st.write(f"Morning: {'Yes' if item['morning'] else 'No'}")
                st.write(f"Afternoon: {'Yes' if item['afternoon'] else 'No'}")
                st.write(f"Night: {'Yes' if item['night'] else 'No'}")

                # Edit medicine schedule in a unique form
                with st.form(f"edit_form_{item['medicine_name']}"):  # Separate form for editing
                    edit_medicine_name = st.text_input("Edit Medicine Name", value=item['medicine_name'])
                    edit_morning_dose = st.checkbox("Edit Morning Dose", value=item['morning'])
                    edit_afternoon_dose = st.checkbox("Edit Afternoon Dose", value=item['afternoon'])
                    edit_night_dose = st.checkbox("Edit Night Dose", value=item['night'])
                    update_submitted = st.form_submit_button("Update")  # Unique submit button

                if update_submitted:
                    updated_schedule = {
                        "medicine_name": edit_medicine_name,
                        "morning": edit_morning_dose,
                        "afternoon": edit_afternoon_dose,
                        "night": edit_night_dose
                    }
                    update_medicine_schedule(st.session_state['user'], item['medicine_name'], updated_schedule)
                    st.success(f"Medicine '{item['medicine_name']}' updated successfully!")

                # Separate form for deletion with unique key
                with st.form(f"delete_form_{item['medicine_name']}"):
                    delete_submitted = st.form_submit_button("Delete")

                if delete_submitted:
                    delete_medicine_schedule(st.session_state['user'], item['medicine_name'])
                    st.success(f"Medicine '{item['medicine_name']}' deleted successfully!")

    # Add Reminder
    st.subheader("Set Reminder for Medicines")
    with st.form("reminder_form"):  # Unique form for reminder
        reminder_medicine_name = st.selectbox("Select medicine", [item['medicine_name'] for item in schedule])
        reminder_time = st.time_input("Reminder Time", datetime.datetime.now().time())
        reminder_submitted = st.form_submit_button("Set Reminder")  # Submit inside form

    if reminder_submitted:
        store_reminder(st.session_state['user'], reminder_medicine_name, reminder_time.strftime("%H:%M"))
        st.success(f"Reminder for '{reminder_medicine_name}' set for {reminder_time.strftime('%H:%M')}")

    # Display current reminders
    st.subheader("Your Reminders")
    reminders = get_reminders(st.session_state['user'])

    if reminders:
        for reminder in reminders:
            reminder_time = datetime.datetime.strptime(reminder[3], "%H:%M").time()

            # Unique form for editing reminders
            with st.expander(f"Reminder: {reminder[2]} at {reminder[3]}", expanded=False):
                with st.form(f"edit_reminder_form_{reminder[0]}"):
                    edit_reminder_time = st.time_input("Edit Reminder Time", value=reminder_time)
                    update_reminder_submitted = st.form_submit_button("Update")

                if update_reminder_submitted:
                    update_reminder(st.session_state['user'], reminder[2], edit_reminder_time.strftime("%H:%M"))
                    st.success(f"Reminder for '{reminder[2]}' updated successfully!")

                # Separate form for deletion
                with st.form(f"delete_reminder_form_{reminder[0]}"):
                    delete_reminder_submitted = st.form_submit_button("Delete")

                if delete_reminder_submitted:
                    delete_reminder(st.session_state['user'], reminder[2])
                    st.success(f"Reminder for '{reminder[2]}' deleted successfully!")
    else:
        st.write("No reminders set. Add reminders above.")



elif page == "Upload":
    if not st.session_state['logged_in']:
        st.warning("You need to log in to access this page.")
        page = "Login"  # Redirect to Login page if not logged in
    else:
        st.header("Medicine Reminder 💊")

    if 'vectorstore' not in st.session_state:
        st.session_state.vectorstore = None

    pdf = st.file_uploader("Upload prescription PDF", type='pdf')

    if pdf is not None:
        pdf_reader = PdfReader(pdf)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_text(text)

        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        st.session_state.vectorstore = FAISS.from_texts(texts, embeddings)

        st.success("PDF uploaded and processed successfully!")

    # Check Medicine Schedule button
    if st.session_state.vectorstore:
        st.subheader("Current Time: " + datetime.datetime.now().strftime("%I:%M %p"))

        # Button to check schedule
        if st.button("Check Medicine Schedule"):
            with st.spinner("Checking schedule..."):
                try:
                    reminder = check_medicine_time(st.session_state.vectorstore)
                    st.write(reminder)
                    if reminder != "No medicines scheduled for now.":
                        if not engine.isBusy():  # Check if engine is not already speaking
                            engine.say(reminder)
                            engine.runAndWait()  # Only run if engine is free
                except Exception as e:
                    st.error(f"Error: {str(e)}")

        # Optionally, you can still have a checkbox for a delay
        auto_check = st.checkbox("Enable automatic checking (every minute)")
        if auto_check:
            while True:
                reminder = check_medicine_time(st.session_state.vectorstore)
                st.write(reminder)
                if not engine.isBusy():  # Ensure engine is free before speaking
                    engine.say(reminder)
                    engine.runAndWait()
                time.sleep(60)  # Sleep for 60 seconds before next check


# Voice Recognition Page
elif page == "Voice Recognition":
    st.header("Voice Recognition Feature")

    # Button to start recording
    if st.button("Start Recording"):
        with sr.Microphone() as source:
            st.write("Adjusting for ambient noise...")
            r.adjust_for_ambient_noise(source)
            st.write("Say something!")
            audio = r.listen(source, timeout=3)  # Record the audio

            try:
                # Recognize speech using Google's Speech-to-Text
                st.write("Recognizing speech...")
                text = r.recognize_google(audio)
                st.write(f"You said: {text}")

                # Save the recognized text to a text file
                with open("recognized_speech.txt", "w") as file:
                    file.write(text)
                st.success("Recognized text has been saved to 'recognized_speech.txt'.")

                # Use recognized text for setting reminders or searching medications
                if 'medicine' in text.lower():
                    st.write("You mentioned a medicine. Would you like to search or set a reminder?")
                    if st.button("Set Reminder for Mentioned Medicine"):
                        st.write(f"Setting a reminder for {text}... (Demo)")

            except sr.UnknownValueError:
                st.error("Google Speech Recognition could not understand the audio.")
            except sr.RequestError as e:
                st.error(f"Could not request results from Google Speech Recognition; {e}")