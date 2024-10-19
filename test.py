import streamlit as st
import speech_recognition as sr

# Initialize the recognizer
r = sr.Recognizer()

st.title("Speech Recognition App")

# Button to start recording
if st.button("Start Recording"):
    with sr.Microphone() as source:
        st.write("Adjusting for ambient noise...")
        r.adjust_for_ambient_noise(source)  # Adjust for ambient noise
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

        except sr.UnknownValueError:
            st.error("Google Speech Recognition could not understand the audio.")
        except sr.RequestError as e:
            st.error(f"Could not request results from Google Speech Recognition; {e}")