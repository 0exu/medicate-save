"""File handling for the Medical Patient Record System.

Each patient is stored in data/patients/P-000001.txt.
The central index is stored in data/master_index.txt.
"""

from pathlib import Path

from records import Patient

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
PATIENT_DIR = DATA_DIR / "patients"
INDEX_FILE = DATA_DIR / "master_index.txt"

INDEX_HEADER = (
    "# patient_id|name|dob|sex|blood_group|phone|diagnoses|vitals|"
    "treatments|last_visit|file"
)

INDEX_FIELDS = (
    "patient_id",
    "name",
    "dob",
    "sex",
    "blood_group",
    "phone",
    "diagnoses",
    "vitals",
    "treatments",
    "last_visit",
    "file",
)


def ensure_files():
    """Create the data folders and an empty index if they do not exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PATIENT_DIR.mkdir(parents=True, exist_ok=True)
    if not INDEX_FILE.exists():
        INDEX_FILE.write_text(INDEX_HEADER + "\n", encoding="utf-8")


def clean(value):
    """Remove characters that would break the pipe-separated file format."""
    return str(value).replace("|", "/").replace("\r", " ").replace("\n", " ").strip()


def number(value):
    """Convert a text field to a float, or return None if it is blank."""
    text = str(value).strip()
    return float(text) if text else None


def number_text(value):
    return "" if value is None else f"{value:g}"


def patient_file(patient_id):
    return PATIENT_DIR / f"{patient_id}.txt"


# ---------------------------------------------------------------------------
# Patient chart files
# ---------------------------------------------------------------------------
def save_patient(patient):
    """Write the complete patient record to their text file."""
    ensure_files()
    lines = []

    lines.append(
        "|".join(
            [
                "PATIENT",
                clean(patient.patient_id),
                clean(patient.name),
                clean(patient.dob),
                clean(patient.sex),
                clean(patient.blood_group),
                clean(patient.phone),
                clean(patient.address),
                clean(patient.allergies),
                clean(patient.registered),
            ]
        )
    )

    for diagnosis in patient.diagnoses:
        lines.append(
            "|".join(
                [
                    "DIAGNOSIS",
                    clean(diagnosis["id"]),
                    clean(diagnosis["date"]),
                    clean(diagnosis["condition"]),
                    clean(diagnosis["severity"]),
                    clean(diagnosis["notes"]),
                ]
            )
        )

    for vitals in patient.vitals:
        lines.append(
            "|".join(
                [
                    "VITALS",
                    clean(vitals["id"]),
                    clean(vitals["date"]),
                    number_text(vitals["temperature"]),
                    number_text(vitals["heart_rate"]),
                    number_text(vitals["systolic"]),
                    number_text(vitals["diastolic"]),
                    number_text(vitals["respiratory_rate"]),
                    number_text(vitals["spo2"]),
                    number_text(vitals["weight"]),
                    number_text(vitals["height"]),
                    number_text(vitals["glucose"]),
                    clean(vitals["notes"]),
                ]
            )
        )

    for treatment in patient.treatments:
        lines.append(
            "|".join(
                [
                    "TREATMENT",
                    clean(treatment["id"]),
                    clean(treatment["date"]),
                    clean(treatment["type"]),
                    clean(treatment["name"]),
                    clean(treatment["dosage"]),
                    clean(treatment["duration"]),
                    clean(treatment["notes"]),
                ]
            )
        )

    path = patient_file(patient.patient_id)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def load_patient(patient_id):
    """Read one patient text file and return a Patient object."""
    ensure_files()
    patient_id = patient_id.strip().upper()
    path = patient_file(patient_id)
    if not path.exists():
        raise FileNotFoundError(f"No record file found for {patient_id}.")

    patient = None
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        parts = line.split("|")
        record_type = parts[0]

        if record_type == "PATIENT":
            patient = Patient(
                patient_id=parts[1],
                name=parts[2],
                dob=parts[3],
                sex=parts[4],
                blood_group=parts[5],
                phone=parts[6],
                address=parts[7],
                allergies=parts[8],
                registered=parts[9] if len(parts) > 9 else "",
            )
        elif record_type == "DIAGNOSIS" and patient is not None:
            patient.diagnoses.append(
                {
                    "id": parts[1],
                    "date": parts[2],
                    "condition": parts[3],
                    "severity": parts[4],
                    "notes": parts[5] if len(parts) > 5 else "",
                }
            )
        elif record_type == "VITALS" and patient is not None:
            patient.vitals.append(
                {
                    "id": parts[1],
                    "date": parts[2],
                    "temperature": number(parts[3]),
                    "heart_rate": number(parts[4]),
                    "systolic": number(parts[5]),
                    "diastolic": number(parts[6]),
                    "respiratory_rate": number(parts[7]),
                    "spo2": number(parts[8]),
                    "weight": number(parts[9]),
                    "height": number(parts[10]),
                    "glucose": number(parts[11]),
                    "notes": parts[12] if len(parts) > 12 else "",
                }
            )
        elif record_type == "TREATMENT" and patient is not None:
            patient.treatments.append(
                {
                    "id": parts[1],
                    "date": parts[2],
                    "type": parts[3],
                    "name": parts[4],
                    "dosage": parts[5],
                    "duration": parts[6],
                    "notes": parts[7] if len(parts) > 7 else "",
                }
            )

    if patient is None:
        raise ValueError(f"Patient file {path.name} is empty or invalid.")

    return patient


def delete_patient(patient_id):
    """Delete the patient's text file."""
    path = patient_file(patient_id)
    if path.exists():
        path.unlink()


# ---------------------------------------------------------------------------
# Master index file
# ---------------------------------------------------------------------------
def make_index_entry(patient):
    diagnoses, vitals, treatments = patient.counts()
    return {
        "patient_id": patient.patient_id,
        "name": patient.name,
        "dob": patient.dob,
        "sex": patient.sex,
        "blood_group": patient.blood_group,
        "phone": patient.phone,
        "diagnoses": diagnoses,
        "vitals": vitals,
        "treatments": treatments,
        "last_visit": patient.last_visit(),
        "file": patient.patient_id + ".txt",
    }


def load_index():
    """Read the master index and return a list of dictionaries."""
    ensure_files()
    entries = []

    for line in INDEX_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        parts = line.split("|")
        if len(parts) < len(INDEX_FIELDS):
            continue

        entries.append(
            {
                "patient_id": parts[0],
                "name": parts[1],
                "dob": parts[2],
                "sex": parts[3],
                "blood_group": parts[4],
                "phone": parts[5],
                "diagnoses": int(parts[6] or 0),
                "vitals": int(parts[7] or 0),
                "treatments": int(parts[8] or 0),
                "last_visit": parts[9],
                "file": parts[10],
            }
        )

    return entries


def save_index(entries):
    """Write all index entries to the master index file."""
    ensure_files()
    lines = [INDEX_HEADER]

    for entry in sorted(entries, key=lambda item: item["patient_id"]):
        lines.append("|".join(clean(entry[field]) for field in INDEX_FIELDS))

    INDEX_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_index(patient):
    """Add or update one patient in the master index."""
    entries = load_index()
    new_entry = make_index_entry(patient)

    for position, entry in enumerate(entries):
        if entry["patient_id"] == patient.patient_id:
            entries[position] = new_entry
            break
    else:
        entries.append(new_entry)

    save_index(entries)


def remove_from_index(patient_id):
    entries = [entry for entry in load_index() if entry["patient_id"] != patient_id]
    save_index(entries)


def rebuild_index():
    """Rebuild the master index by reading every patient text file."""
    ensure_files()
    entries = []

    for path in sorted(PATIENT_DIR.glob("*.txt")):
        try:
            patient = load_patient(path.stem)
        except (FileNotFoundError, ValueError):
            continue
        entries.append(make_index_entry(patient))

    save_index(entries)
    return len(entries)


def find_patients(query):
    """Search the index by patient ID, name or phone number."""
    query = (query or "").strip().lower()
    if not query:
        return []

    matches = []
    for entry in load_index():
        if (
            query in entry["patient_id"].lower()
            or query in entry["name"].lower()
            or query in entry["phone"].lower()
        ):
            matches.append(entry)
    return matches


def next_patient_id():
    """Create the next patient ID, for example P-000004."""
    ensure_files()
    highest = 0

    for entry in load_index():
        try:
            highest = max(highest, int(entry["patient_id"].split("-")[1]))
        except (IndexError, ValueError):
            pass

    for path in PATIENT_DIR.glob("P-*.txt"):
        try:
            highest = max(highest, int(path.stem.split("-")[1]))
        except (IndexError, ValueError):
            pass

    return f"P-{highest + 1:06d}"
