from app import users_col, doctors_col, patients_col, departments_col, appointments_col, treatments_col, str_id, oid
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta, date

def setup_demo():
    print("Setting up expanded premium demo data...")
    
    # 1. Ensure admin exists
    from app import init_db
    init_db()

    # Clear existing demo data (optional, but good for fresh runs)
    # Be careful not to wipe real users if this was a production script, 
    # but since this is mongomock or local test, it's fine to keep adding or just rely on the existing duplicate checks.
    
    departments = list(departments_col.find())
    if not departments:
        print("Error: Departments not found. Run init_db() properly.")
        return

    dept_cardio = next((d for d in departments if d['name'] == 'Cardiology'), departments[0])
    dept_neuro = next((d for d in departments if d['name'] == 'Neurology'), departments[1])
    dept_peds = next((d for d in departments if d['name'] == 'Pediatrics'), departments[2])

    # --- 1. Create Doctors ---
    doctors_data = [
        {
            'username': 'doctor_demo', 'pass': 'doctor123', 'name': 'Dr. Demo Smith', 'email': 'smith@hospital.com',
            'phone': '5551002000', 'dept': str_id(dept_cardio['_id']), 'spec': 'Heart Surgery', 'qual': 'MD, FACS', 'exp': 15
        },
        {
            'username': 'doctor_neuro', 'pass': 'doctor123', 'name': 'Dr. Alice Chen', 'email': 'chen@hospital.com',
            'phone': '5551002001', 'dept': str_id(dept_neuro['_id']), 'spec': 'Neurosurgery', 'qual': 'MD, PhD', 'exp': 12
        },
        {
            'username': 'doctor_peds', 'pass': 'doctor123', 'name': 'Dr. Robert Blake', 'email': 'blake@hospital.com',
            'phone': '5551002002', 'dept': str_id(dept_peds['_id']), 'spec': 'General Pediatrics', 'qual': 'MBBS', 'exp': 8
        }
    ]

    doctor_ids = []
    for d in doctors_data:
        try:
            user = users_col.find_one({'username': d['username']})
            if not user:
                user_id = users_col.insert_one({
                    'username': d['username'], 'password': generate_password_hash(d['pass']), 'role': 'doctor',
                    'name': d['name'], 'email': d['email'], 'phone': d['phone'], 'is_active': True
                }).inserted_id

                doc_id = doctors_col.insert_one({
                    'user_id': str_id(user_id), 'department_id': d['dept'], 'specialization': d['spec'],
                    'qualification': d['qual'], 'experience_years': d['exp']
                }).inserted_id
                doctor_ids.append(str_id(doc_id))
            else:
                doc = doctors_col.find_one({'user_id': str_id(user['_id'])})
                if doc:
                    doctor_ids.append(str_id(doc['_id']))
        except Exception as e:
            print(f"Error inserting doctor {d['username']}: {e}")

    # --- 2. Create Patients ---
    patients_data = [
        {'username': 'patient_demo', 'pass': 'patient123', 'name': 'John Demo Doe', 'email': 'john@demo.com', 'phone': '5552003000', 'dob': '1990-05-15', 'gender': 'Male', 'blood': 'O+', 'address': '123 Demo St'},
        {'username': 'patient_sarah', 'pass': 'patient123', 'name': 'Sarah Connor', 'email': 'sarah@demo.com', 'phone': '5552003001', 'dob': '1985-08-22', 'gender': 'Female', 'blood': 'A-', 'address': '456 Tech Ave'},
        {'username': 'patient_mike', 'pass': 'patient123', 'name': 'Mike Wheeler', 'email': 'mike@demo.com', 'phone': '5552003002', 'dob': '2005-11-03', 'gender': 'Male', 'blood': 'B+', 'address': '789 Maple Rd'},
        {'username': 'patient_emma', 'pass': 'patient123', 'name': 'Emma Watson', 'email': 'emma@demo.com', 'phone': '5552003003', 'dob': '1995-02-14', 'gender': 'Female', 'blood': 'AB+', 'address': '321 Oxford St'},
        {'username': 'patient_james', 'pass': 'patient123', 'name': 'James Bond', 'email': 'james@demo.com', 'phone': '5552003004', 'dob': '1970-07-07', 'gender': 'Male', 'blood': 'O-', 'address': '007 Secret Ln'},
    ]

    patient_ids = []
    for p in patients_data:
        try:
            user = users_col.find_one({'username': p['username']})
            if not user:
                user_id = users_col.insert_one({
                    'username': p['username'], 'password': generate_password_hash(p['pass']), 'role': 'patient',
                    'name': p['name'], 'email': p['email'], 'phone': p['phone'], 'is_active': True
                }).inserted_id

                pat_id = patients_col.insert_one({
                    'user_id': str_id(user_id), 'date_of_birth': p['dob'], 'gender': p['gender'],
                    'address': p['address'], 'blood_group': p['blood']
                }).inserted_id
                patient_ids.append(str_id(pat_id))
            else:
                pat = patients_col.find_one({'user_id': str_id(user['_id'])})
                if pat:
                    patient_ids.append(str_id(pat['_id']))
        except Exception as e:
            print(f"Error inserting patient {p['username']}: {e}")

    # --- 3. Create Appointments ---
    # We will clear existing appointments to prevent massive clutter if script runs multiple times
    appointments_col.delete_many({})
    treatments_col.delete_many({})

    today = date.today()
    
    # Let's generate a mix of completed, booked, and cancelled appointments
    # Ensure we have doctor_ids and patient_ids
    if len(doctor_ids) >= 3 and len(patient_ids) >= 5:
        appts = [
            # Past appointments (Completed)
            (patient_ids[0], doctor_ids[0], today - timedelta(days=5), '09:00', 'Completed', 'Routine checkup. Everything looks fine.', 'Vitamin D 1000IU daily'),
            (patient_ids[1], doctor_ids[1], today - timedelta(days=3), '10:30', 'Completed', 'Migraine complaint. Prescribed painkillers.', 'Ibuprofen 400mg PRN'),
            (patient_ids[2], doctor_ids[2], today - timedelta(days=1), '14:00', 'Completed', 'Mild fever and cough.', 'Paracetamol 500mg, Cough syrup'),
            
            # Today's appointments
            (patient_ids[3], doctor_ids[0], today, '11:00', 'Booked', '', ''),
            (patient_ids[4], doctor_ids[1], today, '15:30', 'Booked', '', ''),
            
            # Future appointments
            (patient_ids[0], doctor_ids[1], today + timedelta(days=1), '09:30', 'Booked', '', ''),
            (patient_ids[1], doctor_ids[2], today + timedelta(days=2), '11:00', 'Booked', '', ''),
            (patient_ids[2], doctor_ids[0], today + timedelta(days=3), '14:30', 'Booked', '', ''),
            (patient_ids[3], doctor_ids[2], today + timedelta(days=5), '10:00', 'Booked', '', ''),
            
            # Cancelled
            (patient_ids[4], doctor_ids[0], today + timedelta(days=4), '16:00', 'Cancelled', '', ''),
        ]

        for pid, did, dt, tm, status, diag, pres in appts:
            apt_id = appointments_col.insert_one({
                'patient_id': pid,
                'doctor_id': did,
                'date': dt.strftime('%Y-%m-%d'),
                'time': tm,
                'status': status,
                'symptoms': 'General consultation',
                'created_at': datetime.now() - timedelta(days=7)
            }).inserted_id

            if status == 'Completed':
                treatments_col.insert_one({
                    'appointment_id': str_id(apt_id),
                    'diagnosis': diag,
                    'prescription': pres,
                    'notes': 'Patient advised to rest.',
                    'created_at': datetime.now() - timedelta(days=1)
                })

    print("Expanded demo data setup complete! The database now has 3 doctors, 5 patients, and 10 appointments.")

if __name__ == '__main__':
    setup_demo()
