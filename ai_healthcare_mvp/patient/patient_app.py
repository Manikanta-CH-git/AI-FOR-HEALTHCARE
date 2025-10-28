import streamlit as st
from datetime import datetime
import os
import firebase_admin
from firebase_admin import credentials, firestore

st.title("🏥 Patient Portal - Recovery & Prescription")

# ✅ Initialize Firebase
cred_path = os.path.join(os.path.dirname(__file__), "..", "firebase_config", "serviceAccountKey.json")
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
db = firestore.client()

# ========================
# ✅ Section 1: Check Prescription
# ========================
st.header("💊 Check Doctor Prescription")

patient_name_check = st.text_input("Enter your name")

if st.button("Check"):
    if patient_name_check.strip() == "":
        st.error("Enter a valid name")
    else:
        docs = db.collection("patients").where("name", "==", patient_name_check).stream()
        found = False
        for doc in docs:
            data = doc.to_dict()
            if data.get("doctor_notes", ""):
                found = True
                st.success(f"📌 Latest Prescription:\n\n{data['doctor_notes']}")
                break

        if not found:
            st.info("No prescription found, doctor not updated yet ✅")

# ========================
# ✅ Section 2: Submit Recovery Data
# ========================
st.header("📝 Submit Today's Recovery Status")

name = st.text_input("Enter your name", key="name_input")
pain = st.slider("Pain Level", 0, 10, 5)
steps = st.number_input("Steps Walked", min_value=0)
medicine = st.selectbox("Medicine Taken?", ["Yes", "No"])
notes = st.text_area("Any Notes for Doctor?")

if st.button("Submit"):
    if name.strip() == "":
        st.error("Enter name")
    else:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # ✅ EXACT same format as doctor
        doc_id = f"{name}_{timestamp}"

        db.collection("patients").document(doc_id).set({
            "name": name,
            "pain_level": pain,
            "steps_walked": steps,
            "medicine_taken": medicine,
            "notes": notes,      # ✅ matches doctor side
            "doctor_notes": "",  # ✅ ensure field exists
            "timestamp": timestamp
        }, merge=True)

        st.success("✅ Submitted Successfully!")
        st.balloons()
