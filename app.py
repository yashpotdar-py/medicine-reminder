from streamlit_option_menu import option_menu
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

# Custom CSS for advanced dark theme styling
st.markdown("""
    <style>
    /* General body styling */
    body {
        font-family: 'Roboto', sans-serif;
        background: linear-gradient(135deg, #1f1f1f, #282828);
    }

    /* Main header styling */
    .main-header {
        color: #FFFFFF;
        text-align: center;
        padding: 30px;
        background: linear-gradient(135deg, #1E88E5, #42A5F5);
        border-radius: 10px;
        font-size: 32px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }

    /* Key features card styling */
    .key-features-card {
        background-color: #333;
        padding: 20px;
        border-radius: 15px;
        margin: 15px 0;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4);
        transition: transform 0.3s ease;
    }

    .key-features-card:hover {
        transform: translateY(-5px);
    }

    .key-features-card p {
        color: #FFFFFF;
        font-size: 18px;
    }

    /* Sidebar styling */
    .css-1aumxhk {
        background-color: #202020;
    }

    .css-1v3fvcr {
        background-color: #1c1c1c;
        color: #f0f0f0;
    }

    /* Button customization */
    .stButton button {
        background-color: #FF5722;
        color: #fff;
        border-radius: 10px;
        transition: background-color 0.3s ease;
        padding: 10px 20px;
        font-size: 16px;
        font-weight: bold;
    }

    .stButton button:hover {
        background-color: #FF7043;
    }

    /* Metrics container */
    .metric-container {
        background-color: #3a3a3a;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4);
    }

    .metric-container h1 {
        color: #29b6f6;
        font-size: 36px;
    }

    /* Graph background */
    .plotly-graph-div {
        background-color: #282828 !important;
    }

    /* Animations for sliders */
    .stSlider > div > div > div > div {
        background-color: #FF5722;
    }

    .stSlider:hover {
        transition: transform 0.2s ease;
        transform: scale(1.02);
    }

    /* Links styling */
    a {
        color: #FF5722;
        text-decoration: none;
    }

    a:hover {
        text-decoration: underline;
    }

    </style>
""", unsafe_allow_html=True)


with st.sidebar:
    page = option_menu(
        "Main Menu",
        ["Home", "Register", "Login", "Dashboard",
            "Schedule & Reminders", "Upload", "Voice Recognition"],
        icons=['house', 'person-plus', 'box-arrow-in-right', 'speedometer2', 'calendar-check', 'cloud-upload', 'mic'],
        menu_icon="capsule",
        default_index=0,
        styles={
            # Dark background
            "container": {"padding": "10!important", "background-color": "#262730", "min-height": "150vh"},
            "icon": {"color": "#FFFFFF", "font-size": "18px"},  # Icon color
            "nav-link": {"font-size": "16px", "color": "#FFFFFF", "text-align": "left", "margin": "0px",
                         "--hover-color": "#262730"},  # Link text color and hover effect
            # Selected item background
            "nav-link-selected": {"background-color": "#1f6feb"}
        }
    )

# Home Page with Enhanced Design
if page == "Home":
    st.markdown("<div class='main-header'>Welcome to Your Medicine Reminder App! 💊</div>",
                unsafe_allow_html=True)

    # Project Overview with Simple Paragraph
    st.subheader("Project Overview")
    st.write("""
            The **Medicine Reminder App** helps manage your medication schedules effectively. 
            It's designed for ease of use, so you never miss a dose. 
            Track, organize, and stay on top of your health!
        """)

    # Simplified CSS for custom styling
    st.markdown("""
        <style>
        /* Styling for the features and benefits sections */
        .section-container {
            background-color: #333;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4);
            transition: transform 0.3s ease;
        }

        .section-container:hover {
            transform: translateY(-5px);
        }

        .section-title {
            color: #FF5722;
            font-size: 24px;
            margin-bottom: 10px;
            font-weight: bold;
        }

        .section-item {
            color: #FFFFFF;
            font-size: 18px;
            margin-bottom: 8px;
        }

        </style>
        """, unsafe_allow_html=True)

    # Main Content for Key Features and Benefits using Streamlit native elements
    st.subheader("Key Features")
    st.markdown("""
            <div class='section-container'>
                <div class='section-item'>💡 <b>User-Friendly Interface:</b> Easy to navigate.</div>
                <div class='section-item'>📆 <b>Medication Schedule:</b> Organize your medications by time.</div>
                <div class='section-item'>🔔 <b>Reminders:</b> Timely notifications to take your meds.</div>
                <div class='section-item'>📄 <b>Upload Prescriptions:</b> Easily store prescription PDFs.</div>
                <div class='section-item'>📊 <b>Overview Dashboard:</b> Visualize your progress.</div>
            </div>
        """, unsafe_allow_html=True)

    st.subheader("Benefits of Using This App")
    st.markdown("""
            <div class='section-container'>
                <div class='section-item'>🗂 <b>Stay Organized:</b> Keep all your medications in one place.</div>
                <div class='section-item'>📅 <b>Improve Adherence:</b> Never miss a dose again.</div>
                <div class='section-item'>📈 <b>Health Insights:</b> Track and analyze your medication habits.</div>
            </div>
        """, unsafe_allow_html=True)

elif page == "Dashboard":
    if not st.session_state['logged_in']:
        st.warning("You need to log in to access the Home page.")
        page = "Login"  # Redirect to the Login page
    else:
        st.markdown("<div class='main-header'>Welcome to Your Medicine Reminder Dashboard! 💊</div>",
                    unsafe_allow_html=True)
        st.subheader("Quick Overview")
        # Simplified CSS for custom styling
        st.markdown("""
        <style>
        /* Styling for the features and benefits sections */
        .section-container {
            background-color: #333;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4);
            transition: transform 0.3s ease;
        }

        .section-container:hover {
            transform: translateY(-5px);
        }

        .section-title {
            color: #FF5722;
            font-size: 24px;
            margin-bottom: 10px;
            font-weight: bold;
        }

        .section-item {
            color: #FFFFFF;
            font-size: 18px;
            margin-bottom: 8px;
        }

        </style>
        """, unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
            st.metric("Total Medicines", "5 medications")  # Update this dynamically if needed
            st.markdown("</div>", unsafe_allow_html=True)
        with col2:
            st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
            st.metric("Active Reminders", "3 reminders")  # Update this dynamically if needed
            st.markdown("</div>", unsafe_allow_html=True)

        st.subheader("Medication Schedule Overview")
        schedule = get_medicine_schedule(st.session_state['user'])
        if schedule:
            data = {
                'Medicine': [],
                'Time': [],
                'Dosage': []  # Include dosage in data
            }
            for item in schedule:
                if item['morning']:
                    data['Medicine'].append(item['medicine_name'])
                    data['Time'].append('Morning')
                    data['Dosage'].append(item['dosage'])
                if item['afternoon']:
                    data['Medicine'].append(item['medicine_name'])
                    data['Time'].append('Afternoon')
                    data['Dosage'].append(item['dosage'])
                if item['night']:
                    data['Medicine'].append(item['medicine_name'])
                    data['Time'].append('Night')
                    data['Dosage'].append(item['dosage'])

            df = pd.DataFrame(data)
            fig = px.histogram(df, x="Time", color="Medicine", barmode="group", y="Dosage",
                               title="Scheduled Medicines Throughout the Day",
                               labels={"Time": "Time of Day",
                                       "Medicine": "Medicine Name",
                                       "Dosage": "Dosage"},  # Updated label
                               category_orders={"Time": ["Morning", "Afternoon", "Night"]})
            st.plotly_chart(fig)
        else:
            st.info("No medication schedule available yet. Add some medications to see insights.")
        st.write("**Explore your reminders, and medication schedule, and stay on top of your health!**")
        st.info("No medication schedule available yet. Add some medications to see insights.")

        # Interactive Buttons with Animations
        st.write("**Explore the features below: (Experminatal)**")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.button("Add a New Medicine 💊")

        with col2:
            st.button("Set New Reminder ⏰")

        with col3:
            st.button("Upload Prescription 📄")

        # Custom Slider with Hover Effect
        st.subheader("Set Custom Dosage Frequency")
        dosage_frequency = st.slider(
            "How frequently do you take your medications? (Times per day)",
            min_value=1, max_value=5, value=3
        )
        st.write(f"Dosage Frequency: {dosage_frequency} times per day.")

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
    if not st.session_state['logged_in']:
        st.warning("You need to log in to access this page.")
        page = "Login"  # Redirect to the Login page
    else:
        st.header("Manage Medication Schedule and Reminders")
        st.subheader("Add Medication Schedule")
        with st.form("medicine_form"):  # Unique form
            medicine_name = st.text_input("Enter the medicine name")
            morning_dose = st.checkbox("Morning")
            afternoon_dose = st.checkbox("Afternoon")
            night_dose = st.checkbox("Night")
            dosage = st.text_input("Enter dosage (e.g. 1 tablet)")  # New dosage input
            submitted = st.form_submit_button("Add Medicine")  # Submit button inside form
        if submitted:
            if medicine_name and dosage:  # Ensure dosage is also provided
                medicine_schedule = {
                    "medicine_name": medicine_name,
                    "morning": morning_dose,
                    "afternoon": afternoon_dose,
                    "night": night_dose,
                    "dosage": dosage  # Include dosage in the schedule
                }
                store_medicine_schedule(st.session_state['user'], medicine_schedule)
                st.success(f"Medicine '{medicine_name}' schedule added successfully!")
            else:
                st.error("Please enter a valid medicine name and dosage.")

        st.subheader("Your Medication Schedule")
        schedule = get_medicine_schedule(st.session_state['user'])
        if schedule:
            for item in schedule:
                with st.expander(f"Medicine: {item['medicine_name']}", expanded=False):
                    st.write(f"Morning: {'Yes' if item['morning'] else 'No'}")
                    st.write(f"Afternoon: {'Yes' if item['afternoon'] else 'No'}")
                    st.write(f"Night: {'Yes' if item['night'] else 'No'}")
                    st.write(f"Dosage: {item['dosage']}")  # Show dosage
                    # Separate form for editing
                    with st.form(f"edit_form_{item['medicine_name']}"):
                        edit_medicine_name = st.text_input("Edit Medicine Name", value=item['medicine_name'])
                        edit_morning_dose = st.checkbox("Edit Morning Dose", value=item['morning'])
                        edit_afternoon_dose = st.checkbox("Edit Afternoon Dose", value=item['afternoon'])
                        edit_night_dose = st.checkbox("Edit Night Dose", value=item['night'])
                        edit_dosage = st.text_input("Edit Dosage", value=item['dosage'])  # Editable dosage field
                        update_submitted = st.form_submit_button("Update")  # Unique submit button
                    if update_submitted:
                        updated_schedule = {
                            "medicine_name": edit_medicine_name,
                            "morning": edit_morning_dose,
                            "afternoon": edit_afternoon_dose,
                            "night": edit_night_dose,
                            "dosage": edit_dosage  # Include updated dosage
                        }
                        update_medicine_schedule(st.session_state['user'], item['medicine_name'], updated_schedule)
                        st.success(f"Medicine '{item['medicine_name']}' updated successfully!")
                    with st.form(f"delete_form_{item['medicine_name']}"):
                        delete_submitted = st.form_submit_button("Delete")
                    if delete_submitted:
                        delete_medicine_schedule(st.session_state['user'], item['medicine_name'])
                        st.success(f"Medicine '{item['medicine_name']}' deleted successfully!")

        st.subheader("Set Reminder for Medicines")
        with st.form("reminder_form"):  # Unique form for reminder
            reminder_medicine_name = st.selectbox("Select medicine", [item['medicine_name'] for item in schedule])
            reminder_time = st.time_input("Reminder Time", datetime.datetime.now().time())
            dosage = next(item[str('dosage')] for item in schedule if item['medicine_name'] == reminder_medicine_name)
            reminder_submitted = st.form_submit_button("Set Reminder")  # Submit inside form
        if reminder_submitted:
            store_reminder(st.session_state['user'], reminder_medicine_name, reminder_time.strftime("%H:%M"), dosage)
            st.success(f"Reminder for '{reminder_medicine_name}' set for {reminder_time.strftime('%H:%M')}")
        
        # Display current reminders
        st.subheader("Your Reminders")
        reminders = get_reminders(st.session_state['user'])

        if reminders:
            for reminder in reminders:
                reminder_time = datetime.datetime.strptime(reminder[3], "%H:%M").time()
                dosage = reminder[4]  # Assuming the dosage is stored in the 5th column of the reminder tuple

                # Unique form for editing reminders
                with st.expander(f"Reminder: {reminder[2]} at {reminder[3]} (Dosage: {dosage})", expanded=False):
                    with st.form(f"edit_reminder_form_{reminder[0]}"):
                        edit_reminder_time = st.time_input("Edit Reminder Time", value=reminder_time)
                        edit_dosage = st.text_input("Edit Dosage", value=dosage)  # Input for dosage
                        update_reminder_submitted = st.form_submit_button("Update")

                    if update_reminder_submitted:
                        update_reminder(
                            st.session_state['user'], reminder[2], edit_reminder_time.strftime("%H:%M"), edit_dosage)
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
        st.header("Upload Prescription (Experimental)")

        if 'vectorstore' not in st.session_state:
            st.session_state.vectorstore = None

        pdf = st.file_uploader("Upload prescription PDF", type='pdf')

        if pdf is not None:
            pdf_reader = PdfReader(pdf)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=200)
            texts = text_splitter.split_text(text)

            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            st.session_state.vectorstore = FAISS.from_texts(texts, embeddings)

            st.success("PDF uploaded and processed successfully!")

        # Check Medicine Schedule button
        if st.session_state.vectorstore:
            st.subheader("Current Time: " +
                         datetime.datetime.now().strftime("%I:%M %p"))

            # Button to check schedule
            if st.button("Check Medicine Schedule"):
                with st.spinner("Checking schedule..."):
                    try:
                        reminder = check_medicine_time(
                            st.session_state.vectorstore)
                        st.write(reminder)
                        if reminder != "No medicines scheduled for now.":
                            if not engine.isBusy():  # Check if engine is not already speaking
                                engine.say(reminder)
                                engine.runAndWait()  # Only run if engine is free
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

            # Optionally, you can still have a checkbox for a delay
            auto_check = st.checkbox(
                "Enable automatic checking (every minute)")
            if auto_check:
                while True:
                    reminder = check_medicine_time(
                        st.session_state.vectorstore)
                    st.write(reminder)
                    if not engine.isBusy():  # Ensure engine is free before speaking
                        engine.say(reminder)
                        engine.runAndWait()
                    time.sleep(60)  # Sleep for 60 seconds before next check


elif page == "Voice Recognition":
    if not st.session_state['logged_in']:
        st.warning("You need to log in to access this page.")
        page = "Login"  # Redirect to the Login page
    else:
        st.header("Voice Recognition (Experimental)")

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
                    st.success(
                        "Recognized text has been saved to 'recognized_speech.txt'.")

                    # Use recognized text for setting reminders or searching medications
                    if 'medicine' in text.lower():
                        st.write(
                            "You mentioned a medicine. Would you like to search or set a reminder?")
                        if st.button("Set Reminder for Mentioned Medicine"):
                            st.write(
                                f"Setting a reminder for {text}... (Demo)")

                except sr.UnknownValueError:
                    st.error(
                        "Google Speech Recognition could not understand the audio.")
                except sr.RequestError as e:
                    st.error(
                        f"Could not request results from Google Speech Recognition; {e}")
