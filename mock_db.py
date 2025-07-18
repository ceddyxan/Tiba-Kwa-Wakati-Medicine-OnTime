# mock_db.py

# Example patient data structure with real data fields for advanced adherence prediction
patients = [
    {
        'name': 'Jane Doe',
        'contact': '+254700000001',
        'age': 55,
        'num_medications': 3,
        'recent_adherence_rate': 0.7,  # e.g., proportion of doses taken in last 7 days
        'feedback_count': 8,           # number of feedback entries in last 7 days
        # ... other fields ...
    },
    # ... more patients ...
]

# When adding or updating a patient, ensure these fields are set and updated as new feedback arrives.
# When retrieving patients for risk prediction, extract these fields for the model input.


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