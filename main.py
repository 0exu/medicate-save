"""Medical Patient Record & History File System.

A simple menu-driven Python mini-project.
Each patient is stored in a separate text file and a central master
index is updated for quick searching.
"""

import records
import storage

VITAL_INPUTS = [
    ("temperature", "Temperature (C)"),
    ("heart_rate", "Heart rate (bpm)"),
    ("systolic", "Systolic BP"),
    ("diastolic", "Diastolic BP"),
    ("respiratory_rate", "Respiratory rate"),
    ("spo2", "SpO2 (%)"),
    ("weight", "Weight (kg)"),
    ("height", "Height (cm)"),
    ("glucose", "Glucose (mg/dL)"),
]


def ask(text, default=""):
    """Ask for text input. Pressing Enter uses the default value."""
    if default:
        text = f"{text} [{default}]"
    value = input(f"{text}: ").strip()
    return value if value else default


def ask_number(label):
    """Ask for a number. A blank answer means skip this value."""
    while True:
        value = input(f"  {label} (blank to skip): ").strip()
        if not value:
            return None
        try:
            return float(value)
        except ValueError:
            print("  Please enter a number or leave blank.")


def show_menu():
    print("\n" + "=" * 52)
    print("   MEDICAL PATIENT RECORD & HISTORY SYSTEM")
    print("=" * 52)
    print("  1.  Add new patient")
    print("  2.  Show all patients")
    print("  3.  Search patient")
    print("  4.  View patient record")
    print("  5.  Add diagnosis")
    print("  6.  Record vitals")
    print("  7.  Add treatment")
    print("  8.  View patient history")
    print("  9.  Delete patient")
    print(" 10.  Rebuild master index")
    print("  0.  Exit")
    print("=" * 52)


def choose_patient():
    """Ask for a patient ID or name and return the patient."""
    query = ask("Patient ID or name")
    if not query:
        print("No patient selected.")
        return None

    matches = storage.find_patients(query)
    if not matches:
        print("Patient not found.")
        return None

    if len(matches) > 1:
        print("\nMultiple patients found:")
        for entry in matches:
            print(f"  {entry['patient_id']} - {entry['name']}")
        patient_id = ask("Enter patient ID").upper()
        matches = [entry for entry in matches if entry["patient_id"] == patient_id]
        if not matches:
            print("Invalid patient ID.")
            return None

    try:
        return storage.load_patient(matches[0]["patient_id"])
    except (FileNotFoundError, ValueError) as error:
        print("Could not load patient:", error)
        return None


def show_all_patients():
    entries = storage.load_index()
    if not entries:
        print("\nNo patients found.")
        return

    print("\n" + "-" * 96)
    print(
        f"{'ID':<10}{'Name':<22}{'Age/Sex':<10}{'Phone':<15}"
        f"{'Dx':>4}{'Vit':>5}{'Rx':>4}  Last visit"
    )
    print("-" * 96)

    for entry in entries:
        age = records.calculate_age(entry["dob"])
        age_sex = f"{age}/{entry['sex']}"
        print(
            f"{entry['patient_id']:<10}{entry['name'][:20]:<22}{age_sex:<10}"
            f"{entry['phone'][:13]:<15}{entry['diagnoses']:>4}"
            f"{entry['vitals']:>5}{entry['treatments']:>4}  {entry['last_visit']}"
        )

    print("-" * 96)
    print(f"Total patients: {len(entries)}")


def search_patient():
    query = ask("Enter ID, name or phone")
    if not query:
        print("Search text is required.")
        return

    matches = storage.find_patients(query)
    if not matches:
        print("No matching patients found.")
        return

    print(f"\nFound {len(matches)} patient(s):")
    for entry in matches:
        print(
            f"  {entry['patient_id']}  {entry['name']}  "
            f"{entry['phone']}  Last visit: {entry['last_visit']}"
        )

    if len(matches) == 1:
        view = ask("View full record? (y/n)", "n").lower()
        if view == "y":
            print_patient(storage.load_patient(matches[0]["patient_id"]))


def view_patient():
    patient = choose_patient()
    if patient is not None:
        print_patient(patient)


def print_patient(patient):
    diagnoses, vitals_count, treatments_count = patient.counts()

    print("\n" + "=" * 78)
    print(f" PATIENT: {patient.name} ({patient.patient_id})")
    print("=" * 78)
    print(
        f" DOB: {patient.dob} ({records.calculate_age(patient.dob)} years)"
        f"   Sex: {patient.sex}   Blood group: {patient.blood_group}"
    )
    print(f" Phone: {patient.phone or '-'}")
    print(f" Address: {patient.address or '-'}")
    print(f" Allergies: {patient.allergies or 'None recorded'}")
    print(f" Registered: {patient.registered}")

    print("-" * 78)
    print(f" DIAGNOSES ({diagnoses})")
    if not patient.diagnoses:
        print("   No diagnoses recorded.")
    for diagnosis in patient.diagnoses:
        print(
            f"   {diagnosis['id']}  {diagnosis['date']}  "
            f"{diagnosis['condition']} [{diagnosis['severity']}]"
        )
        if diagnosis["notes"]:
            print(f"       Notes: {diagnosis['notes']}")

    print("-" * 78)
    print(f" VITALS ({vitals_count})")
    if not patient.vitals:
        print("   No vitals recorded.")
    for vitals in patient.vitals:
        print(
            f"   {vitals['id']}  {vitals['date']}  "
            f"{records.vitals_text(vitals)}"
        )
        warnings = records.vitals_warnings(vitals)
        if warnings:
            print(f"       Warning: {', '.join(warnings)}")
        if vitals["notes"]:
            print(f"       Notes: {vitals['notes']}")

    print("-" * 78)
    print(f" TREATMENTS ({treatments_count})")
    if not patient.treatments:
        print("   No treatments recorded.")
    for treatment in patient.treatments:
        print(
            f"   {treatment['id']}  {treatment['date']}  "
            f"{treatment['type']}  {treatment['name']}"
        )
        extra = []
        if treatment["dosage"]:
            extra.append("Dosage: " + treatment["dosage"])
        if treatment["duration"]:
            extra.append("Duration: " + treatment["duration"])
        if extra:
            print("       " + " | ".join(extra))
        if treatment["notes"]:
            print(f"       Notes: {treatment['notes']}")

    print("=" * 78)


def add_patient():
    print("\n--- Add New Patient ---")
    name = ask("Full name")
    if not name:
        print("Name is required.")
        return

    dob = ask("Date of birth (YYYY-MM-DD)")
    try:
        dob = records.check_date(dob, default_today=False)
    except ValueError as error:
        print("Error:", error)
        return

    sex = ask("Sex (M/F/O/U)", "U").upper()
    blood_group = ask("Blood group", "Unknown")
    phone = ask("Phone")
    address = ask("Address")
    allergies = ask("Allergies", "None")

    patient = records.Patient(
        patient_id=storage.next_patient_id(),
        name=name,
        dob=dob,
        sex=sex,
        blood_group=blood_group,
        phone=phone,
        address=address,
        allergies=allergies,
    )
    storage.save_patient(patient)
    storage.update_index(patient)
    print(f"\nPatient added successfully. ID: {patient.patient_id}")


def add_diagnosis():
    patient = choose_patient()
    if patient is None:
        return

    condition = ask("Diagnosis / condition")
    if not condition:
        print("Diagnosis is required.")
        return

    severity = ask("Severity (Mild/Moderate/Severe/Critical)", "Moderate")
    date_text = ask("Date (YYYY-MM-DD)", records.today_text())
    notes = ask("Notes")

    try:
        diagnosis = records.add_diagnosis(
            patient, condition, severity, date_text, notes
        )
    except ValueError as error:
        print("Error:", error)
        return

    storage.save_patient(patient)
    storage.update_index(patient)
    print(f"\nDiagnosis {diagnosis['id']} added to {patient.name}.")


def add_vitals():
    patient = choose_patient()
    if patient is None:
        return

    print("\nEnter vitals. Leave blank to skip a value.")
    values = {}
    for key, label in VITAL_INPUTS:
        values[key] = ask_number(label)

    notes = ask("Notes")
    date_text = ask("Date (YYYY-MM-DD)", records.today_text())

    try:
        vitals = records.add_vitals(patient, values, notes, date_text)
    except ValueError as error:
        print("Error:", error)
        return

    storage.save_patient(patient)
    storage.update_index(patient)
    print(f"\nVitals {vitals['id']} recorded for {patient.name}.")

    warnings = records.vitals_warnings(vitals)
    if warnings:
        print("Warning:", ", ".join(warnings))


def add_treatment():
    patient = choose_patient()
    if patient is None:
        return

    name = ask("Treatment name")
    if not name:
        print("Treatment name is required.")
        return

    treatment_type = ask(
        "Type (Medication/Procedure/Surgery/Therapy/Lifestyle/Observation)",
        "Medication",
    )
    date_text = ask("Date (YYYY-MM-DD)", records.today_text())
    dosage = ask("Dosage")
    duration = ask("Duration")
    notes = ask("Notes")

    try:
        treatment = records.add_treatment(
            patient, name, treatment_type, date_text, dosage, duration, notes
        )
    except ValueError as error:
        print("Error:", error)
        return

    storage.save_patient(patient)
    storage.update_index(patient)
    print(f"\nTreatment {treatment['id']} added to {patient.name}.")


def show_history():
    patient = choose_patient()
    if patient is None:
        return

    events = records.history(patient)
    print(f"\nHistory for {patient.name} ({patient.patient_id})")
    print("-" * 78)

    if not events:
        print("No history recorded yet.")
        return

    for event in events:
        print(f"{event['date']}  {event['type']:<10} {event['summary']}")
        if event["details"]:
            print(f"           {event['details']}")


def delete_patient():
    patient = choose_patient()
    if patient is None:
        return

    answer = ask(f"Delete {patient.name} ({patient.patient_id})? (y/n)", "n").lower()
    if answer != "y":
        print("Cancelled.")
        return

    storage.delete_patient(patient.patient_id)
    storage.remove_from_index(patient.patient_id)
    print("Patient deleted.")


def rebuild_index():
    count = storage.rebuild_index()
    print(f"\nMaster index rebuilt. {count} patient file(s) indexed.")


def main():
    storage.ensure_files()

    while True:
        show_menu()
        choice = ask("Enter your choice")

        if choice == "1":
            add_patient()
        elif choice == "2":
            show_all_patients()
        elif choice == "3":
            search_patient()
        elif choice == "4":
            view_patient()
        elif choice == "5":
            add_diagnosis()
        elif choice == "6":
            add_vitals()
        elif choice == "7":
            add_treatment()
        elif choice == "8":
            show_history()
        elif choice == "9":
            delete_patient()
        elif choice == "10":
            rebuild_index()
        elif choice == "0":
            print("\nThank you for using the Medical Patient Record System.")
            break
        else:
            print("Invalid choice. Please enter a number from 0 to 10.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nProgram stopped.")
