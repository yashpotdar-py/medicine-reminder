import sys
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

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = "AIzaSyDgsUUAeA9sBwKBzz20cAxCyI0dY-g_CPU"

engine = pyttsx3.init()


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
    "Select a Page:", ["Home", "Login", "Register", "Schedule & Reminders", 'Upload'])

# Home Page
if page == "Home":
    if not st.session_state['logged_in']:
        st.warning("You need to log in to access the home page.")
        page = "Login"  # Redirect to Login page if not logged in

    if st.session_state['logged_in']:
        st.title("Welcome to Medicine Reminder App!")
        st.write("This is your home page. Please use the features provided.")

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

# Overhauled Schedule & Reminders Page
elif page == "Schedule & Reminders":
    if not st.session_state['logged_in']:
        st.warning("You need to log in to access this page.")
        page = "Login"  # Redirect to Login page if not logged in
    else:
        st.header("Manage Medication Schedule and Reminders")

        # Add Medication Schedule
        st.subheader("Add Medication Schedule")
        with st.form("medicine_form"):
            medicine_name = st.text_input("Enter the medicine name")
            morning_dose = st.checkbox("Morning")
            afternoon_dose = st.checkbox("Afternoon")
            night_dose = st.checkbox("Night")
            submitted = st.form_submit_button("Add Medicine")

        if submitted:
            if medicine_name:
                medicine_schedule = {
                    "medicine_name": medicine_name,
                    "morning": morning_dose,
                    "afternoon": afternoon_dose,
                    "night": night_dose
                }
                store_medicine_schedule(
                    st.session_state['user'], medicine_schedule)
                st.success(
                    f"Medicine '{medicine_name}' schedule added successfully!")
            else:
                st.error("Please enter a valid medicine name.")

        # Display current medication schedule
        st.subheader("Your Medication Schedule")
        schedule = get_medicine_schedule(st.session_state['user'])

        if schedule:
            for item in schedule:
                with st.expander(f"Medicine: {item['medicine_name']}", expanded=False):
                    st.write(f"Morning: {'Yes' if item['morning'] else 'No'}")
                    st.write(
                        f"Afternoon: {'Yes' if item['afternoon'] else 'No'}")
                    st.write(f"Night: {'Yes' if item['night'] else 'No'}")

                    # Edit medicine schedule
                    edit_medicine_name = st.text_input(
                        "Edit Medicine Name", value=item['medicine_name'])
                    edit_morning_dose = st.checkbox(
                        "Edit Morning Dose", value=item['morning'])
                    edit_afternoon_dose = st.checkbox(
                        "Edit Afternoon Dose", value=item['afternoon'])
                    edit_night_dose = st.checkbox(
                        "Edit Night Dose", value=item['night'])

                    if st.button("Update", key=f"update_{item['medicine_name']}"):
                        updated_schedule = {
                            "medicine_name": edit_medicine_name,
                            "morning": edit_morning_dose,
                            "afternoon": edit_afternoon_dose,
                            "night": edit_night_dose
                        }
                        update_medicine_schedule(
                            st.session_state['user'], item['medicine_name'], updated_schedule)
                        st.success(
                            f"Medicine '{item['medicine_name']}' updated successfully!")

                    if st.button("Delete", key=f"delete_{item['medicine_name']}"):
                        delete_medicine_schedule(
                            st.session_state['user'], item['medicine_name'])
                        st.success(
                            f"Medicine '{item['medicine_name']}' deleted successfully!")

        # Add Reminder
        st.subheader("Set Reminder for Medicines")
        with st.form("reminder_form"):
            reminder_medicine_name = st.selectbox(
                "Select medicine", [item['medicine_name'] for item in schedule])
            reminder_time = st.time_input(
                "Reminder Time", datetime.now().time())
            reminder_submitted = st.form_submit_button("Set Reminder")

        if reminder_submitted:
            store_reminder(st.session_state['user'],
                           reminder_medicine_name, reminder_time.strftime("%H:%M"))
            st.success(
                f"Reminder for '{reminder_medicine_name}' set for {reminder_time.strftime('%H:%M')}")

        # Display current reminders
        st.subheader("Your Reminders")
        reminders = get_reminders(st.session_state['user'])

        if reminders:
            for reminder in reminders:
                reminder_time = datetime.strptime(reminder[3], "%H:%M").time()

                with st.expander(f"Reminder: {reminder[2]} at {reminder[3]}", expanded=False):
                    # Edit reminder
                    edit_reminder_time = st.time_input(
                        "Edit Reminder Time", value=reminder_time)

                    # Use reminder ID to make key unique
                    if st.button("Update", key=f"update_reminder_{reminder[0]}"):
                        update_reminder(
                            st.session_state['user'], reminder[2], edit_reminder_time.strftime("%H:%M"))
                        st.success(
                            f"Reminder for '{reminder[2]}' updated successfully!")

                    if st.button("Delete", key=f"delete_reminder_{reminder[0]}"):
                        delete_reminder(st.session_state['user'], reminder[2])
                        st.success(
                            f"Reminder for '{reminder[2]}' deleted successfully!")
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
                        engine.say(reminder)
                        engine.runAndWait()
                except Exception as e:
                    st.error(f"Error: {str(e)}")

        # Optionally, you can still have a checkbox for a delay
        auto_check = st.checkbox("Enable automatic checking (every minute)")
        if auto_check:
            if 'last_checked' not in st.session_state:
                st.session_state['last_checked'] = datetime.datetime.now()

            current_time = datetime.datetime.now()
            time_difference = (
                current_time - st.session_state['last_checked']).total_seconds()

            if time_difference >= 60:  # Check every minute
                with st.spinner("Checking schedule..."):
                    try:
                        reminder = check_medicine_time(
                            st.session_state.vectorstore)
                        st.write(reminder)
                        if reminder != "No medicines scheduled for now.":
                            engine.say(reminder)
                            engine.runAndWait()
                        st.session_state['last_checked'] = current_time
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
