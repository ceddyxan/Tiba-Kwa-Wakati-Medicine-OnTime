# ml_model.py
import pandas as pd
import numpy as np

def predict_nonadherence(patient_contact, feedback_log, window=5):
    # Filter feedback for this patient
    patient_feedback = [f for f in feedback_log if f["patient_contact"] == patient_contact]
    if not patient_feedback:
        return 0.0  # No data, assume low risk
    df = pd.DataFrame(patient_feedback)
    # Consider only last 'window' feedbacks
    df = df.tail(window)
    # Count 'no' and 'delay' as non-adherence
    nonadherent = df["response"].isin(["no", "delay"]).sum()
    risk = nonadherent / len(df)
    return risk


def risk_trend(patient_contact, feedback_log, window=5):
    # Returns a list of risk scores over time (rolling window)
    patient_feedback = [f for f in feedback_log if f["patient_contact"] == patient_contact]
    if not patient_feedback:
        return []
    df = pd.DataFrame(patient_feedback)
    if "timestamp" in df:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp")
    # Encode response: 1 for non-adherence, 0 for adherence
    df["nonadherent"] = df["response"].isin(["no", "delay"]).astype(int)
    # Rolling mean (risk) over time
    df["risk"] = df["nonadherent"].rolling(window, min_periods=1).mean()
    return list(zip(df["timestamp"].astype(str), df["risk"]))


def detect_anomalies(patient_contact, feedback_log, window=5):
    """
    Detects sudden jumps in risk (e.g., >0.5 increase or low to high risk).
    Returns a list of (timestamp, description) for each anomaly detected.
    """
    trend = risk_trend(patient_contact, feedback_log, window)
    anomalies = []
    if len(trend) < 2:
        return anomalies
    prev_risk = trend[0][1]
    for i in range(1, len(trend)):
        ts, risk = trend[i]
        if (risk - prev_risk) > 0.5:
            anomalies.append((ts, f"Sudden risk increase: {prev_risk:.2f} → {risk:.2f}"))
        if prev_risk < 0.33 and risk > 0.66:
            anomalies.append((ts, f"Risk jump from low to high: {prev_risk:.2f} → {risk:.2f}"))
        prev_risk = risk
    return anomalies 