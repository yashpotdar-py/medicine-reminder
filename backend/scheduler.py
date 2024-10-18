import schedule
import time
from backend.reminders import text_to_speech_reminder  # Your text-to-speech reminder function

# Sample reminder function for medicine
def medicine_reminder(medicine_name, username):
    reminder_message = f"Time to take your medicine: {medicine_name}"
    print(reminder_message)
    text_to_speech_reminder(reminder_message)  # Optionally play the reminder using text-to-speech

# Schedule a reminder based on user input
def schedule_medicine_reminder(medicine_schedule, username):
    if medicine_schedule['morning']:
        schedule.every().day.at("23:53").do(medicine_reminder, medicine_schedule['medicine_name'], username)
    
    if medicine_schedule['afternoon']:
        schedule.every().day.at("14:00").do(medicine_reminder, medicine_schedule['medicine_name'], username)
    
    if medicine_schedule['night']:
        schedule.every().day.at("00:00").do(medicine_reminder, medicine_schedule['medicine_name'], username)

# Start the scheduler
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)
