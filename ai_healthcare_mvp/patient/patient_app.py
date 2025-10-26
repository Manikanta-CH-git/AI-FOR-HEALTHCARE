import streamlit as st
import pandas as pd
from datetime import datetime
import os
import firebase_admin
from firebase_admin import credentials, firestore

st.title("Patient Portal - Recovery & Prescription")

# -----------------------------
# Initialize Firebase
# -----------------------------
cred_path = os.path.join(os.path.dirname(__file__), "..", "firebase_config", "serviceAccountKey.json")
cred = credentials.Certificate(cred_path)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

# -----------------------------
# Part 1: Prescription Check
# -----------------------------
st.header("💊 Check Prescription / Doctor Notes")
check_name = st.text_input("Enter your name to check prescription", key="check_name")

if st.button("Check Prescription"):
    if not check_name:
        st.error("Please enter your name!")
    else:
        # Query Firebase for documents matching the patient name
        docs = db.collection("patients").where("name", "==", check_name).stream()
        records = [doc.to_dict() for doc in docs]
        
        if records:
            st.success(f"Found {len(records)} record(s) for {check_name}:")
            for rec in records:
                st.markdown(f"""
                *Date:* {rec.get('timestamp', 'N/A')}  
                *Pain Level:* {rec.get('pain_level', 'N/A')}  
                *Steps Walked:* {rec.get('steps_walked', 'N/A')}  
                *Medicine Taken:* {rec.get('medicine_taken', 'N/A')}  
                *Patient Notes:* {rec.get('patient_notes', 'N/A')}  
                *Doctor Prescription / Notes:* {rec.get('doctor_notes', 'Not yet provided')}
                """)
        else:
            st.warning("No records found. Please submit your daily report below.")

# -----------------------------
# Part 2: Daily Recovery Submission
# -----------------------------
st.header("📝 Submit Daily Recovery Data")
name = st.text_input("Enter your name", key="submit_name")
pain = st.slider("Pain level (1 = low, 10 = high)", 1, 10)
steps = st.number_input("Steps walked today", min_value=0, step=100)
medicine = st.selectbox("Took medicine today?", ["Yes", "No"])
patient_notes = st.text_area("Additional notes (optional)")

if st.button("Submit Daily Report"):
    if not name:
        st.error("Please enter your name!")
    else:
        timestamp = datetime.now().isoformat()
        doc_id = f"{name}_{timestamp}"

        patient_data = {
            "timestamp": timestamp,
            "name": name,
            "pain_level": pain,
            "steps_walked": steps,
            "medicine_taken": medicine,  # Only patient input
            "patient_notes": patient_notes,
            "doctor_notes": ""  # Will be filled separately by doctor
        }

        db.collection("patients").document(doc_id).set(patient_data)
        st.success(f"Daily report submitted successfully ✅")
        st.balloons()