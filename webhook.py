from flask import Flask, request, Response
from mock_db import add_feedback, get_patients, get_schedules
import datetime

app = Flask(__name__)

@app.route('/feedback', methods=['POST'])
def feedback():
    from_number = request.form.get('From')
    body = request.form.get('Body', '').strip().lower()
    # Try to match patient by phone number
    patient = next((p for p in get_patients() if p['contact'] in from_number), None)
    if not patient:
        return Response('<Response><Message>Patient not found.</Message></Response>', mimetype='text/xml')
    # Try to match medication (optional: could parse from message)
    schedules = [s for s in get_schedules() if s['patient_contact'] == patient['contact']]
    if not schedules:
        return Response('<Response><Message>No medication schedule found.</Message></Response>', mimetype='text/xml')
    # For simplicity, log feedback for all medications for this patient
    for sched in schedules:
        feedback = {
            'patient_contact': patient['contact'],
            'medication': sched['medication'],
            'timestamp': datetime.datetime.now().isoformat(),
            'response': body if body in ['yes', 'no', 'delay'] else 'unknown',
        }
        add_feedback(feedback)
    return Response('<Response><Message>Thank you for your feedback!</Message></Response>', mimetype='text/xml')

if __name__ == '__main__':
    app.run(port=5000) 