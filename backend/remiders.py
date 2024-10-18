import pyttsx3
import time

def text_to_speech_reminder(medicine_name, dosage):
    engine = pyttsx3.init()
    engine.setProperty('rate', 185)  # Set speech rate (default is 200)
    reminder_message = f"It is time to take {dosage} of {medicine_name}"
    
    for _ in range(3):  # Repeat the message 3 times
        engine.say(reminder_message)
        engine.runAndWait()
        time.sleep(1)  # Delay of 1 second between reminders

if __name__ == "__main__":
    text_to_speech_reminder("utkarsh", 2)
