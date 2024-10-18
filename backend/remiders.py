import pyttsx3

def text_to_speech_reminder(medicine_name, dosage):
    engine = pyttsx3.init()
    reminder_message = f"It is time to take {dosage} of {medicine_name}."
    engine.say(reminder_message)
    engine.runAndWait()
