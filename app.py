import streamlit as st
import pandas as pd
from mock_db import add_patient, get_patients, add_schedule, get_schedules, add_feedback, get_feedback
from ml_model import predict_nonadherence, risk_trend, detect_anomalies
import datetime
from translate import translate
import scheduler
from datetime import datetime, time
import re

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
st.sidebar.info("Created for Kenya, Uganda, Tanzania, Rwanda 🇰🇪🇺🇬🇹🇿🇷🇼")

# --- Main Tabs ---
tabs = st.tabs(["🏠 Home", "➕ Register", "📊 Dashboard"])

# --- Home Tab ---
with tabs[0]:
    st.markdown("""
    <h1 style='text-align: center; color: #2E86C1;'>Tiba Kwa Wakati 💊</h1>
    <h4 style='text-align: center; color: #117A65;'>Your smart, multilingual medicine reminder for East Africa</h4>
    <div style='text-align: center;'>
        <img src='https://cdn.pixabay.com/photo/2017/01/31/13/14/medicine-2028240_1280.png' width='200'/>
    </div>
    <br>
    <p style='text-align: center;'>Easily register patients, send reminders in their language, and track adherence with AI-powered insights.</p>
    """, unsafe_allow_html=True)
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
    with st.form("register_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("👤 Patient Name")
            contact = st.text_input("📱 Phone Number (with country code)")
            country = st.selectbox("🌍 Country", COUNTRIES)
            start_date = st.date_input("📅 Start Date", value=datetime.today())
        with col2:
            language = st.selectbox("🗣️ Preferred Language", LANGUAGES)
            medication_select = st.selectbox("💊 Medication Name (search or select)", chronic_meds, index=0)
            medication = medication_select
            custom_med = ""
            if medication_select == "Other (type below)":
                custom_med = st.text_input("💊 Enter Medication Name (if not in list)")
                medication = custom_med
            # 24-hour time picker only
            med_time = st.time_input("⏰ Time (24-hour format)", value=time(8,0))
            # (Removed AM/PM radio)
        submitted = st.form_submit_button("Register Patient")
        # Validation
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
                # Convert time to 12-hour format with AM/PM
                hour = med_time.hour
                minute = med_time.minute
                # (Removed AM/PM logic)
                schedule_str = f"{hour:02d}:{minute:02d}"
                patient = {
                    "name": name,
                    "contact": contact,
                    "country": country,
                    "language": language,
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
                        st.experimental_rerun()
        st.markdown("---")

# --- Footer ---
st.markdown("""
    <hr style='border:1px solid #eee;'>
    <div style='text-align:center; color: #888;'>
        Made with ❤️ for East Africa | Powered by Streamlit & AI | <a href='mailto:support@tibakwawakati.com'>Contact Support</a>
    </div>
    """, unsafe_allow_html=True) 