from apscheduler.schedulers.background import BackgroundScheduler
import time

scheduler = BackgroundScheduler()

def schedule_reminder(user_id, reminder_time, medicine_name, dosage):
    def reminder():
        print(f"Reminder for user {user_id}: Time to take {dosage} of {medicine_name}!")
    
    scheduler.add_job(reminder, 'date', run_date=reminder_time)
    scheduler.start()

def stop_scheduler():
    scheduler.shutdown()
