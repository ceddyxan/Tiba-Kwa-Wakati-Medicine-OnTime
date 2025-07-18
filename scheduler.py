# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from mock_db import get_schedules, get_patients, patients
from messaging import send_sms, send_whatsapp, send_voice
from translate import translate
import datetime
from reminder_optimization import PersonalizedBandit
import random

scheduler = BackgroundScheduler()

# Supported channels
CHANNELS = ["SMS", "WhatsApp", "Voice"]

# Define possible reminder strategies (arms)
arms = [
    ("SMS", "8am", "friendly"),
    ("WhatsApp", "6pm", "urgent"),
    ("Voice", "12pm", "simple"),
]
bandit = PersonalizedBandit(arms)

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
                # Select best arm for this patient
                arm_index = bandit.select_arm(patient["contact"])
                channel, time, message_type = arms[arm_index]
                msg = translate(f"Hello {patient['name']}, it's time to take your {sched['medication']}!", patient["language"])
                # Schedule/send reminder using selected parameters (mocked)
                print(f"Scheduling {channel} reminder at {time} with '{message_type}' message for {patient['name']}")
                send_sms(patient["contact"], msg)
                send_whatsapp(patient["contact"], msg)
                send_voice(patient["contact"], msg)
                # After feedback is received (mocked here)
                feedback = random.choice([0, 1])  # 1=adhered, 0=not
                bandit.update(patient["contact"], arm_index, feedback)
                print(f"Feedback received: {'adhered' if feedback else 'not adhered'}")

# Start the scheduler
scheduler.add_job(check_and_send_reminders, 'interval', minutes=1)

def start():
    if not scheduler.running:
        scheduler.start()

def recommend_optimal_time(adherence_history, times):
    """
    Recommend the best time based on adherence history.
    adherence_history: list of 0/1 (1=adhered, 0=missed), ordered by times
    times: list of time strings corresponding to adherence_history
    Returns: recommended time string
    """
    if not adherence_history or not times or len(adherence_history) != len(times):
        return times[0] if times else "8am"
    # Group by time and compute adherence rate
    from collections import defaultdict
    time_stats = defaultdict(lambda: [0, 0])  # time -> [taken, total]
    for t, a in zip(times, adherence_history):
        time_stats[t][1] += 1
        if a:
            time_stats[t][0] += 1
    rates = {t: taken/total if total else 0 for t, (taken, total) in time_stats.items()}
    # Recommend time with highest adherence rate
    return max(rates, key=rates.get)

# Example: show recommended time in dashboard (pseudo-code, adapt as needed)
for patient in patients:
    history = patient.get('adherence_history', [1, 0, 1, 0, 1, 1])
    times = patient.get('dose_times', ['8am', '8pm', '8am', '8pm', '8am', '8pm'])
    recommended_time = recommend_optimal_time(history, times)
    print(f"Recommended optimal time for {patient['name']}: {recommended_time}") 