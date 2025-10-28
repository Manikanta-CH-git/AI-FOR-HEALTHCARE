import streamlit as st
import pandas as pd
import os
import sys
import firebase_admin
from firebase_admin import credentials, firestore

# -----------------------------
# Fix Python path to include utils
# -----------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.risk_calculator import ai_health_risk_score

# -----------------------------
# Initialize Firebase (safe)
# -----------------------------
cred_path = os.path.join(os.path.dirname(__file__), "..", "firebase_config", "serviceAccountKey.json")
cred = credentials.Certificate(cred_path)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

st.title("🩺 Doctor Dashboard - AI Recovery Monitoring")

# -----------------------------
# Fetch patients from Firestore
# -----------------------------
docs = db.collection("patients").stream()
data = [doc.to_dict() for doc in docs]
if not data:
    st.warning("No patient data found.")
    st.stop()

df = pd.DataFrame(data)
df['name'] = df['name'].fillna("Unknown")

# -----------------------------
# AI Risk Computation
# -----------------------------
ai_results = []
for _, row in df.iterrows():
    try:
        ai_output = ai_health_risk_score(
            steps=row.get("steps_walked", 0),
            pain_level=row.get("pain_level", 5),
            medicine_taken=row.get("medicine_taken", "No") == "Yes",
            sleep_hours=row.get("sleep_hours", None),
            mood=row.get("mood", None)
        )
        ai_results.append({
            "Name": row["name"],
            "Pain": row.get("pain_level", 0),
            "Steps": row.get("steps_walked", 0),
            "Medicine": row.get("medicine_taken", "No"),
            "Notes": row.get("notes", ""),
            "Doctor_Notes": row.get("doctor_notes", ""),
            "Timestamp": row.get("timestamp", ""),
            "AI_Risk_Score": ai_output["risk_score"],
            "AI_Risk_Level": ai_output["risk_level"],
            "AI_Recommendation": ai_output["ai_recommendation"]
        })
    except Exception as e:
        st.error(f"Error processing {row['name']}: {e}")

df_ai = pd.DataFrame(ai_results)
df_ai = df_ai.sort_values(by="AI_Risk_Score", ascending=False)

st.subheader("📋 Patient Status Overview")

# -----------------------------
# Display AI Cards and Update Option
# -----------------------------
for _, row in df_ai.iterrows():
    color = "#90EE90"  # Low Risk
    if row["AI_Risk_Level"] == "High":
        color = "#FF6347"
    elif row["AI_Risk_Level"] == "Moderate":
        color = "#FFA500"

    with st.container():
        st.markdown(
            f"""
            <div style="
                background-color: {color};
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 10px;
            ">
                <h4>{row['Name']} — <b>{row['AI_Risk_Level']} Risk ({row['AI_Risk_Score']})</b></h4>
                <p><b>Pain:</b> {row['Pain']} | <b>Steps:</b> {row['Steps']} | <b>Medicine:</b> {row['Medicine']}</p>
                <p><b>AI Recommendation:</b> {row['AI_Risk_Recommendation'] if 'AI_Risk_Recommendation' in row else row['AI_Recommendation']}</p>
                <p><b>Patient Notes:</b> {row['Notes']}</p>
                <p><b>Doctor Notes / Prescription:</b> {row['Doctor_Notes']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Doctor input field
        new_doctor_notes = st.text_area(
            f"✏ Write/Update Prescription for {row['Name']}",
            value=row["Doctor_Notes"],
            key=f"doc_notes_{row['Timestamp']}"
        )

        # Update Firestore
        if st.button(f"✅ Save Prescription for {row['Name']}", key=f"save_{row['Timestamp']}"):
            doc_ref = db.collection("patients").where("timestamp", "==", row["Timestamp"]).stream()
            found = False

            for doc in doc_ref:
                doc.reference.update({"doctor_notes": new_doctor_notes})
                found = True

            if found:
                st.success(f"✅ Prescription updated for {row['Name']}")
            else:
                st.error(f"❌ Could not find matching timestamp record!")
