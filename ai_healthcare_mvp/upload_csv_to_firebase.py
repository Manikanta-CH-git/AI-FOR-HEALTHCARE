import csv
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
cred = credentials.Certificate("firebase_config/serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

csv_file_path = "data/patient_data.csv"

with open(csv_file_path, mode='r', encoding='utf-8') as csvfile:
    # ✅ delimiter=',' and quotechar='"' are important
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        clean_row = {k.strip(): v.strip() for k, v in row.items() if k}

        # Convert numeric fields
        for field in ['pain_level', 'steps_walked']:
            if field in clean_row:
                clean_row[field] = int(clean_row[field])

        # Use patient name as unique document ID to prevent duplicates
        db.collection("patients").document(clean_row['name']).set(clean_row)
        print(f"✅ Uploaded: {clean_row}")

print("🎉 All patient data uploaded successfully without mix-ups!")