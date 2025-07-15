# mock_db.py

patients = []  # List of patient dicts
schedules = []  # List of schedule dicts
feedback_log = []  # List of feedback dicts


def add_patient(patient):
    patients.append(patient)
    return patient


def get_patients():
    return patients


def add_schedule(schedule):
    schedules.append(schedule)
    return schedule


def get_schedules():
    return schedules


def add_feedback(feedback):
    feedback_log.append(feedback)
    return feedback


def get_feedback(patient_contact=None):
    if patient_contact:
        return [f for f in feedback_log if f["patient_contact"] == patient_contact]
    return feedback_log 