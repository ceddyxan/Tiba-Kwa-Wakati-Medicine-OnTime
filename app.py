import streamlit as st
import pandas as pd
from mock_db import add_patient, get_patients, add_schedule, get_schedules, add_feedback, get_feedback
from ml_model import predict_nonadherence, risk_trend, detect_anomalies, predict_adherence_risk, predict_dropout_risk, suggest_interventions
import datetime
from translate import translate
import scheduler
from datetime import datetime, time
import re
from forecasting import forecast_adherence_arima
from feedback_analysis import analyze_feedback
from anomaly_detection import detect_anomalies_kmeans
from scheduler import recommend_optimal_time
import altair as alt

# Supported countries and languages
COUNTRIES = ["Kenya", "Uganda", "Tanzania", "Rwanda"]
LANGUAGES = ["English", "Swahili", "Kinyarwanda", "Luganda"]

# --- Sidebar ---
st.set_page_config(page_title="Tiba Kwa Wakati", layout="wide", page_icon="💊")
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2965/2965567.png", width=80)
st.sidebar.title("Tiba Kwa Wakati")
st.sidebar.markdown("""
**Multilingual AI-powered medicine reminder system for East Africa.**

- Register patients & schedules
- Automated reminders
- AI-powered adherence prediction
- Visual dashboard
""")
st.sidebar.info("Created for Kenya, Uganda, Tanzania, Rwanda")

# --- Main Tabs ---
tabs = st.tabs(["🏠 Home", "➕ Register", "📊 Dashboard"])

# --- Home Tab ---
with tabs[0]:
    st.markdown("""
    <h1 style='text-align: center; color: #2E86C1;'>Tiba Kwa Wakati 💊</h1>
    <h4 style='text-align: center; color: #117A65;'>Your smart, multilingual medicine reminder for East Africa</h4>
    <br>
    <p style='text-align: center;'>Easily register patients, send reminders in their language, and track adherence with AI-powered insights.</p>
    """, unsafe_allow_html=True)
    st.image(
        "https://images.unsplash.com/photo-1511174511562-5f7f18b874f8?auto=format&fit=crop&w=400&q=80",
        width=200,
        caption="Medicine Reminder",
        align="center"
    )
    st.success("Get started by registering a patient or viewing the dashboard.")
    
# --- Register Tab ---
with tabs[1]:
    st.header("➕ Register Patient & Medication Schedule")
    chronic_meds = [
        "Tenofovir (HIV)", "Lamivudine (HIV)", "Efavirenz (HIV)",
        "Metformin (Diabetes)", "Insulin (Diabetes)", "Glibenclamide (Diabetes)",
        "Amlodipine (Hypertension)", "Lisinopril (Hypertension)", "Hydrochlorothiazide (Hypertension)",
        "Isoniazid (TB)", "Rifampicin (TB)", "Ethambutol (TB)", "Pyrazinamide (TB)",
        "Other (type below)"
    ]
    # Patient Registration Form (initial version)
    st.header("Patient Registration")
    with st.form("register_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("👤 Patient Name")
            contact = st.text_input("📱 Phone Number (with country code)")
            country = st.selectbox("🌍 Country", COUNTRIES)
            start_date = st.date_input("📅 Start Date", value=datetime.today())
            age = st.number_input("Age", min_value=0, max_value=120, value=30)
        with col2:
            language = st.selectbox("🗣️ Preferred Language", LANGUAGES)
            medication_select = st.selectbox("💊 Medication Name (search or select)", chronic_meds, index=0)
            medication = medication_select
            custom_med = ""
            if medication_select == "Other (type below)":
                custom_med = st.text_input("💊 Enter Medication Name (if not in list)")
                medication = custom_med
            med_time = st.time_input("⏰ Time (24-hour format)", value=time(8,0))
            num_medications = st.number_input("Number of Medications", min_value=1, max_value=20, value=1)
        submitted = st.form_submit_button("Register Patient")
        errors = []
        if submitted:
            if not name:
                errors.append("Patient Name is required.")
            if not contact:
                errors.append("Phone Number is required.")
            if not country:
                errors.append("Country is required.")
            if not language:
                errors.append("Language is required.")
            if medication_select == "Other (type below)" and not custom_med:
                errors.append("Please enter the medication name if it's not in the list.")
            if not med_time:
                errors.append("Time is required.")
            if not start_date:
                errors.append("Start Date is required.")
            if errors:
                for err in errors:
                    st.error(err)
            else:
                hour = med_time.hour
                minute = med_time.minute
                schedule_str = f"{hour:02d}:{minute:02d}"
                patient = {
                    "name": name,
                    "contact": contact,
                    "country": country,
                    "language": language,
                    "age": age,
                    "num_medications": num_medications,
                }
                add_patient(patient)
                sched = {
                    "patient_contact": contact,
                    "medication": medication,
                    "schedule": schedule_str,
                    "start_date": str(start_date),
                }
                add_schedule(sched)
                st.success(f"✅ Registered {name} for {medication} reminders starting {start_date} at {med_time.strftime('%I:%M')}.")
    st.markdown("---")
    st.subheader("👥 Registered Patients")
    patients = get_patients()
    if patients:
        df_patients = pd.DataFrame(patients)
        st.dataframe(df_patients, use_container_width=True)
    else:
        st.info("No patients registered yet.")
    st.markdown("---")
    st.subheader("💊 Medication Schedules")
    schedules = get_schedules()
    if schedules:
        df_sched = pd.DataFrame(schedules)
        st.dataframe(df_sched, use_container_width=True)
    else:
        st.info("No medication schedules yet.")

# --- Dashboard Tab ---
with tabs[2]:
    st.header("📊 Healthcare Worker Dashboard")
    patients = get_patients()
    schedules = get_schedules()
    feedback_log = get_feedback()

    # Filters
    with st.expander("🔎 Filter Patients", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            country_filter = st.selectbox("🌍 Country", ["All"] + COUNTRIES)
        with col2:
            language_filter = st.selectbox("🗣️ Language", ["All"] + LANGUAGES)
        with col3:
            medications = list({s['medication'] for s in schedules})
            med_filter = st.selectbox("💊 Medication", ["All"] + medications)
    filtered_patients = [p for p in patients if (country_filter == "All" or p["country"] == country_filter) and (language_filter == "All" or p["language"] == language_filter)]

    # Metrics
    st.markdown("---")
    st.subheader("📈 Adherence Metrics")
    total_patients = len(filtered_patients)
    total_feedback = len(feedback_log)
    avg_risk = 0.0
    if total_patients > 0:
        avg_risk = sum([predict_nonadherence(p["contact"], feedback_log) for p in filtered_patients]) / total_patients
    col1, col2, col3 = st.columns(3)
    col1.metric("👥 Patients", total_patients)
    col2.metric("📝 Feedback Entries", total_feedback)
    col3.metric("⚠️ Avg. Risk", f"{avg_risk:.2f}", delta=None, delta_color="inverse")

    # Feedback log table
    st.markdown("---")
    st.subheader("📝 Feedback Log")
    if feedback_log:
        df_feedback = pd.DataFrame(feedback_log)
        if med_filter != "All":
            df_feedback = df_feedback[df_feedback["medication"] == med_filter]
        if country_filter != "All":
            df_feedback = df_feedback[df_feedback["patient_contact"].isin([p["contact"] for p in filtered_patients])]
        st.dataframe(df_feedback, use_container_width=True)
    else:
        st.info("No feedback logged yet.")

    # Risk levels and adherence trends
    st.markdown("---")
    st.subheader("⚠️ Adherence Risk & Trends")
    for patient in filtered_patients:
        risk = predict_nonadherence(patient["contact"], feedback_log)
        color = "🟢" if risk < 0.33 else ("🟡" if risk < 0.66 else "🔴")
        st.markdown(f"**{patient['name']} ({patient['contact']})** - Risk: {color} <span style='font-size:1.2em'>{round(risk,2)}</span>", unsafe_allow_html=True)
        trend = risk_trend(patient["contact"], feedback_log)
        if trend:
            trend_df = pd.DataFrame(trend, columns=["Timestamp", "Risk"])
            st.line_chart(trend_df.set_index("Timestamp"))
        # Show recent feedback for this patient
        patient_feedback = [f for f in feedback_log if f["patient_contact"] == patient["contact"]]
        if patient_feedback:
            with st.expander("Recent Feedback", expanded=False):
                st.dataframe(pd.DataFrame(patient_feedback).tail(5), use_container_width=True)
        # Anomaly detection alerts
        anomalies = detect_anomalies(patient["contact"], feedback_log)
        if anomalies:
            for ts, desc in anomalies:
                st.warning(f"🚨 Anomaly detected on {ts}: {desc}")
        # Feedback logging form for each medication
        patient_schedules = [s for s in schedules if s["patient_contact"] == patient["contact"]]
        for sched in patient_schedules:
            # Use contact, schedule time, and start date as unique form key
            safe_schedule = re.sub(r'[^a-zA-Z0-9]', '_', sched['schedule'])
            safe_date = re.sub(r'[^a-zA-Z0-9]', '_', sched.get('start_date', ''))
            form_key = f"feedback_{patient['contact']}_{safe_schedule}_{safe_date}"
            # Only show feedback form if no feedback exists for today for this patient/medication/schedule
            today = datetime.now().date().isoformat()
            feedback_exists = any(
                f["patient_contact"] == patient["contact"] and
                f["medication"] == sched["medication"] and
                f["timestamp"].startswith(today) and
                sched["schedule"] in form_key and
                safe_date in form_key
                for f in feedback_log
            )
            if not feedback_exists:
                with st.form(form_key, clear_on_submit=True):
                    st.write(f"Log feedback for **{sched['medication']}** at {sched['schedule']}:")
                    response = st.selectbox("Did the patient take the medication?", ["yes", "no", "delay"])
                    submitted = st.form_submit_button("Log Feedback")
                    if submitted:
                        feedback = {
                            "patient_contact": patient["contact"],
                            "medication": sched["medication"],
                            "timestamp": datetime.now().isoformat(),
                            "response": response,
                        }
                        add_feedback(feedback)
                        st.success("Feedback logged.")
                        # st.experimental_rerun()  # Removed due to AttributeError in current Streamlit version
        st.markdown("---")

    st.header("Advanced Adherence Prediction (All Patients)")
    risk_data = []
    feature_importances = {}
    for patient in patients:
        # Calculate recent adherence rate
        adherence_history = patient.get('adherence_history', [])
        if adherence_history:
            recent_adherence_rate = sum(adherence_history[-7:]) / min(len(adherence_history), 7)
        else:
            recent_adherence_rate = 0.0
        # Calculate feedback count in last 7 days
        feedback_count = 0
        now = datetime.now()
        for feedback in feedback_log:
            if feedback.get('patient_contact') == patient['contact']:
                ts = feedback.get('timestamp')
                if ts and isinstance(ts, datetime) and (now - ts).days < 7:
                    feedback_count += 1
        features = [
            recent_adherence_rate,
            patient.get('age', 40),
            patient.get('num_medications', 2),
            feedback_count
        ]
        prob, label, importance = predict_adherence_risk(features)
        risk_data.append({'Patient': patient['name'], 'Risk Probability': prob, 'Risk Level': 'High' if label else 'Low'})
        feature_importances[patient['name']] = importance

    df_risk = pd.DataFrame(risk_data).sort_values('Risk Probability', ascending=False)

    # Add a color column based on risk probability

    def risk_color(prob):
        if prob > 0.7:
            return 'High'
        elif prob > 0.4:
            return 'Medium'
        else:
            return 'Low'

    df_risk['RiskColor'] = df_risk['Risk Probability'].apply(risk_color)
    color_scale = alt.Scale(domain=['High', 'Medium', 'Low'], range=['red', 'orange', 'green'])

    chart = alt.Chart(df_risk).mark_bar().encode(
        x=alt.X('Risk Probability:Q', scale=alt.Scale(domain=[0, 1])),
        y=alt.Y('Patient:N', sort='-x'),
        color=alt.Color('RiskColor:N', scale=color_scale, legend=alt.Legend(title="Risk Level")),
        tooltip=['Patient', 'Risk Probability', 'Risk Level']
    ).properties(height=400)
    st.altair_chart(chart, use_container_width=True)

    # Sortable, color-coded table
    def color_risk(val):
        if val > 0.7:
            color = 'red'
        elif val > 0.4:
            color = 'orange'
        else:
            color = 'green'
        return f'background-color: {color}'

    st.dataframe(df_risk.style.applymap(color_risk, subset=['Risk Probability']))

    # Expanders for per-patient feature importance
    for patient in df_risk['Patient']:
        with st.expander(f"Feature Importance for {patient}"):
            imp = feature_importances[patient]
            sorted_imp = sorted(imp.items(), key=lambda x: x[1], reverse=True)
            for fname, score in sorted_imp:
                st.write(f"- {fname}: {score:.2f}")

    st.header("Personalized Adherence Forecast (All Patients)")
    forecast_dict = {}
    for patient in patients:
        history = patient.get('adherence_history', [1, 1, 0, 1, 1, 0, 1])
        forecast = forecast_adherence_arima(history, steps=7)
        forecast_dict[patient['name']] = forecast
    if forecast_dict:
        df_forecast = pd.DataFrame(forecast_dict)
        df_forecast.index = [f"Day {i+1}" for i in range(7)]
        st.line_chart(df_forecast)

    st.header("Recent Patient Feedback Analysis")
    # Example: assume feedback_log is a list of dicts with 'patient', 'text', and 'timestamp'
    for feedback in feedback_log[-10:]:  # Show last 10 feedback entries
        analysis = analyze_feedback(feedback.get('text', ''))
        st.subheader(f"Feedback from {feedback['patient_contact']} at {feedback['timestamp']}")
        st.write(f"Text: {feedback.get('text', '')}")
        st.write(f"Sentiment: {analysis['sentiment']} (polarity: {analysis['polarity']:.2f})")
        st.write(f"Detected Intents: {', '.join(analysis['intents'])}")
        if analysis['flag']:
            st.markdown("**:red[Flagged for review]**")

    st.header("Anomaly & Event Detection")
    # Assume adherence_histories is a list of all patients' adherence histories
    adherence_histories = [p.get('adherence_history', [1,1,1,1,1,1,1]) for p in patients]
    anomalies = detect_anomalies_kmeans(adherence_histories)
    for patient, is_anomaly in zip(patients, anomalies):
        if is_anomaly:
            st.warning(f"Anomaly detected in adherence for {patient['name']}")

    st.header("Predictive Analytics & Interventions")
    for patient in patients:
        # Calculate recent adherence rate
        adherence_history = patient.get('adherence_history', [])
        if adherence_history:
            recent_adherence_rate = sum(adherence_history[-7:]) / min(len(adherence_history), 7)
        else:
            recent_adherence_rate = 0.0
        # Calculate feedback count in last 7 days
        feedback_count = 0
        now = datetime.now()
        for feedback in feedback_log:
            if feedback.get('patient_contact') == patient['contact']:
                ts = feedback.get('timestamp')
                if ts and isinstance(ts, datetime) and (now - ts).days < 7:
                    feedback_count += 1
        negative_feedback_count = patient.get('negative_feedback_count', 0)
        prob, label = predict_dropout_risk(recent_adherence_rate, negative_feedback_count)
        st.subheader(f"Patient: {patient['name']}")
        st.write(f"Dropout/complication risk: {prob:.2f} ({'High' if label else 'Low'})")
        feedback_analysis = patient.get('last_feedback_analysis', {'intents': []})
        interventions = suggest_interventions(label, feedback_analysis)
        st.write("Suggested interventions:")
        for intervention in interventions:
            st.write(f"- {intervention}")

    st.header("AI-Driven Scheduling Recommendations")
    for patient in patients:
        history = patient.get('adherence_history', [1, 0, 1, 0, 1, 1])
        times = patient.get('dose_times', ['8am', '8pm', '8am', '8pm', '8am', '8pm'])
        recommended_time = recommend_optimal_time(history, times)
        st.write(f"Recommended optimal time for {patient['name']}: {recommended_time}")

# --- Footer ---
st.markdown("""
    <hr style='border:1px solid #eee;'>
    <div style='text-align:center; color: #888;'>
        Made with ❤️ for East Africa | Powered by Streamlit & AI | <a href='mailto:support@tibakwawakati.com'>Contact Support</a>
    </div>
    """, unsafe_allow_html=True)