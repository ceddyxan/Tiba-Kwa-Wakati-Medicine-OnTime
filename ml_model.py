# ml_model.py
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.ensemble import RandomForestClassifier

# Mock data for demonstration (replace with real data integration)
# Features: [recent_adherence_rate, age, num_medications, feedback_count]
X = np.array([
    [0.9, 35, 1, 10],
    [0.7, 60, 3, 8],
    [0.5, 50, 2, 5],
    [0.2, 40, 4, 2],
    [0.95, 30, 1, 12],
    [0.4, 70, 5, 3],
    [0.8, 55, 2, 9],
    [0.3, 65, 4, 4],
    [0.6, 45, 3, 6],
    [0.85, 38, 1, 11],
])
# Labels: 1 = high risk, 0 = low risk
Y = np.array([0, 1, 1, 1, 0, 1, 0, 1, 1, 0])

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

# Train logistic regression model
model = LogisticRegression()
model.fit(X_train, y_train)

def predict_adherence_risk(features):
    """
    Predicts the risk of non-adherence for a patient.
    Args:
        features (list): [recent_adherence_rate, age, num_medications, feedback_count]
    Returns:
        risk_prob (float): Probability of high risk
        risk_label (int): 1 = high risk, 0 = low risk
        feature_importance (dict): Feature importance scores
    """
    risk_prob = model.predict_proba([features])[0][1]
    risk_label = int(risk_prob > 0.5)
    # Feature importance (absolute value of coefficients)
    feature_names = ['recent_adherence_rate', 'age', 'num_medications', 'feedback_count']
    importance = dict(zip(feature_names, np.abs(model.coef_[0])))
    return risk_prob, risk_label, importance

# Example usage:
if __name__ == "__main__":
    print("Classification report on test set:")
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred))
    # Predict for a new patient
    features = [0.6, 50, 2, 7]
    prob, label, importance = predict_adherence_risk(features)
    print(f"Predicted risk probability: {prob:.2f}, High risk: {label}")
    print("Feature importance:", importance)


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

# Example: Dropout/complication risk prediction
# Mock data for demonstration
X_risk = [
    [0.9, 0],  # [recent_adherence_rate, negative_feedback_count]
    [0.7, 2],
    [0.5, 4],
    [0.2, 6],
    [0.95, 0],
    [0.4, 5],
    [0.8, 1],
    [0.3, 7],
    [0.6, 3],
    [0.85, 0],
]
Y_risk = [0, 1, 1, 1, 0, 1, 0, 1, 1, 0]  # 1 = high risk
risk_model = RandomForestClassifier(random_state=42)
risk_model.fit(X_risk, Y_risk)

def predict_dropout_risk(recent_adherence_rate, negative_feedback_count):
    prob = risk_model.predict_proba([[recent_adherence_rate, negative_feedback_count]])[0][1]
    label = int(prob > 0.5)
    return prob, label

def suggest_interventions(risk_label, feedback_analysis):
    interventions = []
    if risk_label:
        interventions.append("Schedule follow-up call")
    if 'side_effects' in feedback_analysis.get('intents', []):
        interventions.append("Review medication for side effects")
    if 'confused' in feedback_analysis.get('intents', []):
        interventions.append("Clarify instructions with patient")
    if 'cost' in feedback_analysis.get('intents', []):
        interventions.append("Discuss cost-saving options")
    if not interventions:
        interventions.append("Continue routine monitoring")
    return interventions

# Example usage:
if __name__ == "__main__":
    prob, label = predict_dropout_risk(0.5, 3)
    print(f"Dropout/complication risk: {prob:.2f}, High risk: {label}")
    feedback = {'intents': ['side_effects', 'confused']}
    print("Suggested interventions:", suggest_interventions(label, feedback)) 