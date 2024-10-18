import pyttsx3  # Simple text-to-speech engine
import time
def text_to_speech_reminder(text):
    for i in range(3):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        time.sleep(1)  # Wait for 1 second before the next reminder

