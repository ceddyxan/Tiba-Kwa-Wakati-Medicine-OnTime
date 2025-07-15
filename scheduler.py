# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from mock_db import get_schedules, get_patients
from messaging import send_sms, send_whatsapp, send_voice
from translate import translate
import datetime

scheduler = BackgroundScheduler()

# Supported channels
CHANNELS = ["SMS", "WhatsApp", "Voice"]

# Helper to parse schedule times (e.g., '8:00, 20:00')
def parse_times(times_str):
    return [t.strip() for t in times_str.split(",") if t.strip()]

def check_and_send_reminders():
    now = datetime.datetime.now().strftime("%H:%M")
    schedules = get_schedules()
    patients = get_patients()
    for sched in schedules:
        times = parse_times(sched["schedule"])
        if now in times:
            patient = next((p for p in patients if p["contact"] == sched["patient_contact"]), None)
            if patient:
                msg = translate(f"Hello {patient['name']}, it's time to take your {sched['medication']}!", patient["language"])
                # For demo, send via all channels (mocked)
                send_sms(patient["contact"], msg)
                send_whatsapp(patient["contact"], msg)
                send_voice(patient["contact"], msg)

# Start the scheduler
scheduler.add_job(check_and_send_reminders, 'interval', minutes=1)

def start():
    if not scheduler.running:
        scheduler.start() 