# Tiba Kwa Wakati

A multilingual AI-powered medicine reminder system for East Africa (Kenya, Uganda, Tanzania, Rwanda).

## Overview
Tiba Kwa Wakati is a demo healthcare platform that helps patients remember to take their medication on time, in their preferred language, and enables healthcare workers to monitor adherence. The system uses AI to predict non-adherence risk and supports SMS, WhatsApp, and voice reminders (mocked for demo/testing).

## Features
- Patient registration and medication scheduling
- Multilingual reminders (SMS, WhatsApp, Voice) [mocked]
- Patient feedback logging (via dashboard or webhook)
- AI-powered adherence prediction and anomaly detection
- Dashboard for healthcare workers with metrics and trends
- Language support: English, Swahili, Kinyarwanda, Luganda

## Architecture
- **Streamlit App (`app.py`)**: Main UI for registration, scheduling, dashboard, and feedback logging.
- **Mock Database (`mock_db.py`)**: In-memory storage for patients, schedules, and feedback.
- **Messaging (`messaging.py`)**: Mocked Twilio integration for SMS, WhatsApp, and voice reminders.
- **Scheduler (`scheduler.py`)**: Periodically checks schedules and sends reminders.
- **Translation (`translate.py`)**: Uses Google Translate API for multilingual support.
- **AI Model (`ml_model.py`)**: Simple risk scoring and anomaly detection for adherence.
- **Webhook (`webhook.py`)**: Flask endpoint to receive patient feedback via SMS/WhatsApp.

## Quickstart (Mock Version)
1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   streamlit run app.py
   ```
3. (Optional) Start the webhook for feedback:
   ```bash
   python webhook.py
   ```

## Usage
- Register patients and medication schedules via the Streamlit UI.
- Reminders are sent (mocked) at scheduled times in the patient's preferred language.
- Log feedback via the dashboard or by sending 'yes', 'no', or 'delay' to the webhook endpoint.
- Healthcare workers can view adherence metrics, risk trends, and feedback logs.

## Extending the System
- **Production Messaging**: Replace `messaging.py` mocks with real Twilio credentials.
- **Persistent Database**: Swap `mock_db.py` for a real database (e.g., PostgreSQL, MongoDB).
- **Deployment**: Deploy Streamlit and Flask apps to cloud platforms for real-world use.

## API/Webhook
- `POST /feedback` (Flask): Accepts feedback from patients via SMS/WhatsApp. Expects `From` (phone) and `Body` (feedback: 'yes', 'no', 'delay').

## File Descriptions
- `app.py`: Main Streamlit app (UI, registration, dashboard)
- `mock_db.py`: In-memory mock database
- `messaging.py`: Mocked Twilio messaging (SMS, WhatsApp, Voice)
- `scheduler.py`: Reminder scheduling logic
- `translate.py`: Google Translate integration
- `ml_model.py`: Adherence risk and anomaly detection
- `webhook.py`: Flask webhook for patient feedback

## Notes
- Messaging and database are mocked for easy testing.
- Replace `mock_db.py` and `messaging.py` with real integrations as needed.
- For demo only. Not for clinical use. 