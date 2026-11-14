"""Record logic for the Medical Patient Record System.

This file contains the Patient class and the functions that add
diagnoses, vitals and treatments. It also does the simple validation
and calculates warnings for abnormal vitals.
"""

from datetime import date, datetime

SEVERITIES = ("Mild", "Moderate", "Severe", "Critical")
TREATMENT_TYPES = (
    "Medication",
    "Procedure",
    "Surgery",
    "Therapy",
    "Lifestyle",
    "Observation",
)

# (lowest allowed value, highest allowed value, label)
VITAL_LIMITS = {
    "temperature": (30.0, 45.0, "Temperature"),
    "heart_rate": (20, 300, "Heart rate"),
    "systolic": (50, 300, "Systolic pressure"),
    "diastolic": (20, 200, "Diastolic pressure"),
    "respiratory_rate": (5, 80, "Respiratory rate"),
    "spo2": (50, 100, "SpO2"),
    "weight": (0.5, 500, "Weight"),
    "height": (20, 300, "Height"),
    "glucose": (10, 1000, "Glucose"),
}


class Patient:
    """A patient and all of their medical records."""

    def __init__(
        self,
        patient_id,
        name,
        dob,
        sex,
        blood_group="Unknown",
        phone="",
        address="",
        allergies="",
        registered=None,
    ):
        self.patient_id = patient_id
        self.name = name
        self.dob = dob
        self.sex = sex
        self.blood_group = blood_group
        self.phone = phone
        self.address = address
        self.allergies = allergies
        self.registered = registered or today_text()

        self.diagnoses = []
        self.vitals = []
        self.treatments = []

    def counts(self):
        """Return the number of diagnoses, vitals records and treatments."""
        return len(self.diagnoses), len(self.vitals), len(self.treatments)

    def last_visit(self):
        """Return the date of the latest medical record."""
        dates = [item["date"] for item in self.diagnoses]
        dates += [item["date"] for item in self.vitals]
        dates += [item["date"] for item in self.treatments]
        return max(dates) if dates else self.registered


def today_text():
    return date.today().isoformat()


def calculate_age(dob):
    """Calculate age from a date of birth in YYYY-MM-DD format."""
    try:
        born = datetime.strptime(dob, "%Y-%m-%d").date()
    except ValueError:
        return "?"
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def check_date(text, default_today=True):
    """Check a date and return it as YYYY-MM-DD."""
    text = (text or "").strip()
    if not text:
        if default_today:
            return today_text()
        raise ValueError("Date is required.")

    try:
        value = datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Date must be in YYYY-MM-DD format.")

    if value > date.today():
        raise ValueError("Date cannot be in the future.")

    return value.isoformat()


def next_id(records, prefix):
    """Create the next ID such as D-0001, V-0001 or T-0001."""
    highest = 0
    for record in records:
        try:
            number = int(record["id"].split("-")[1])
            highest = max(highest, number)
        except (KeyError, IndexError, ValueError):
            pass
    return f"{prefix}-{highest + 1:04d}"


def add_diagnosis(patient, condition, severity, date_text, notes=""):
    condition = condition.strip()
    if not condition:
        raise ValueError("Diagnosis cannot be empty.")

    severity = (severity or "Moderate").strip().title()
    if severity not in SEVERITIES:
        raise ValueError("Severity must be Mild, Moderate, Severe or Critical.")

    diagnosis = {
        "id": next_id(patient.diagnoses, "D"),
        "date": check_date(date_text),
        "condition": condition,
        "severity": severity,
        "notes": notes.strip(),
    }
    patient.diagnoses.append(diagnosis)
    return diagnosis


def add_vitals(patient, values, notes="", date_text=""):
    """Add a vitals record. Values is a dictionary of measurements."""
    measured = {key: value for key, value in values.items() if value is not None}
    if not measured:
        raise ValueError("Enter at least one vital measurement.")

    for key, value in measured.items():
        low, high, label = VITAL_LIMITS[key]
        if value < low or value > high:
            raise ValueError(f"{label} must be between {low:g} and {high:g}.")

    systolic = values.get("systolic")
    diastolic = values.get("diastolic")
    if systolic is not None and diastolic is not None and diastolic > systolic:
        raise ValueError("Diastolic pressure cannot be higher than systolic pressure.")

    vitals = {
        "id": next_id(patient.vitals, "V"),
        "date": check_date(date_text),
        "notes": notes.strip(),
    }
    for key in VITAL_LIMITS:
        vitals[key] = values.get(key)

    patient.vitals.append(vitals)
    return vitals


def add_treatment(patient, name, treatment_type, date_text, dosage="", duration="", notes=""):
    name = name.strip()
    if not name:
        raise ValueError("Treatment name cannot be empty.")

    treatment_type = (treatment_type or "Medication").strip().title()
    if treatment_type not in TREATMENT_TYPES:
        raise ValueError(
            "Treatment type must be Medication, Procedure, Surgery, "
            "Therapy, Lifestyle or Observation."
        )

    treatment = {
        "id": next_id(patient.treatments, "T"),
        "date": check_date(date_text),
        "type": treatment_type,
        "name": name,
        "dosage": dosage.strip(),
        "duration": duration.strip(),
        "notes": notes.strip(),
    }
    patient.treatments.append(treatment)
    return treatment


def calculate_bmi(weight, height):
    if weight is None or height is None or height == 0:
        return None
    height_in_metres = height / 100
    return round(weight / (height_in_metres * height_in_metres), 1)


def number_text(value):
    if value is None:
        return "?"
    return f"{value:g}"


def vitals_text(vitals):
    """Return a short one-line summary of a vitals record."""
    parts = []

    if vitals["temperature"] is not None:
        parts.append("Temp " + number_text(vitals["temperature"]) + " C")
    if vitals["heart_rate"] is not None:
        parts.append("HR " + number_text(vitals["heart_rate"]))
    if vitals["systolic"] is not None or vitals["diastolic"] is not None:
        parts.append(
            "BP "
            + number_text(vitals["systolic"])
            + "/"
            + number_text(vitals["diastolic"])
        )
    if vitals["respiratory_rate"] is not None:
        parts.append("RR " + number_text(vitals["respiratory_rate"]))
    if vitals["spo2"] is not None:
        parts.append("SpO2 " + number_text(vitals["spo2"]) + "%")
    if vitals["weight"] is not None:
        parts.append("Weight " + number_text(vitals["weight"]) + " kg")
    if vitals["height"] is not None:
        parts.append("Height " + number_text(vitals["height"]) + " cm")
    if vitals["glucose"] is not None:
        parts.append("Glucose " + number_text(vitals["glucose"]) + " mg/dL")

    bmi = calculate_bmi(vitals["weight"], vitals["height"])
    if bmi is not None:
        parts.append("BMI " + str(bmi))

    return ", ".join(parts) if parts else "No measurements"


def vitals_warnings(vitals):
    """Return warning messages for abnormal but possible values."""
    warnings = []

    temperature = vitals["temperature"]
    if temperature is not None:
        if temperature >= 38.0:
            warnings.append("Fever")
        elif temperature <= 35.0:
            warnings.append("Low body temperature")

    heart_rate = vitals["heart_rate"]
    if heart_rate is not None:
        if heart_rate > 100:
            warnings.append("Fast heart rate")
        elif heart_rate < 60:
            warnings.append("Slow heart rate")

    systolic = vitals["systolic"]
    diastolic = vitals["diastolic"]
    if (systolic is not None and systolic >= 140) or (
        diastolic is not None and diastolic >= 90
    ):
        warnings.append("High blood pressure")
    elif (systolic is not None and systolic < 90) or (
        diastolic is not None and diastolic < 60
    ):
        warnings.append("Low blood pressure")

    respiratory_rate = vitals["respiratory_rate"]
    if respiratory_rate is not None:
        if respiratory_rate > 20:
            warnings.append("Fast breathing")
        elif respiratory_rate < 12:
            warnings.append("Slow breathing")

    spo2 = vitals["spo2"]
    if spo2 is not None and spo2 < 95:
        warnings.append("Low oxygen saturation")

    glucose = vitals["glucose"]
    if glucose is not None:
        if glucose < 70:
            warnings.append("Low glucose")
        elif glucose > 180:
            warnings.append("High glucose")

    bmi = calculate_bmi(vitals["weight"], vitals["height"])
    if bmi is not None:
        if bmi < 18.5:
            warnings.append("Underweight")
        elif bmi >= 30:
            warnings.append("Obese")

    return warnings


def history(patient):
    """Combine diagnoses, vitals and treatments into one timeline."""
    events = []

    for diagnosis in patient.diagnoses:
        details = diagnosis["severity"]
        if diagnosis["notes"]:
            details += " - " + diagnosis["notes"]
        events.append(
            {
                "date": diagnosis["date"],
                "type": "Diagnosis",
                "summary": diagnosis["condition"],
                "details": details,
            }
        )

    for vitals in patient.vitals:
        details = vitals_text(vitals)
        warnings = vitals_warnings(vitals)
        if warnings:
            details += " | Warning: " + ", ".join(warnings)
        events.append(
            {
                "date": vitals["date"],
                "type": "Vitals",
                "summary": "Vitals recorded",
                "details": details,
            }
        )

    for treatment in patient.treatments:
        details = treatment["type"]
        if treatment["dosage"]:
            details += " - Dosage: " + treatment["dosage"]
        if treatment["duration"]:
            details += " - Duration: " + treatment["duration"]
        if treatment["notes"]:
            details += " - " + treatment["notes"]
        events.append(
            {
                "date": treatment["date"],
                "type": "Treatment",
                "summary": treatment["name"],
                "details": details,
            }
        )

    events.sort(key=lambda event: event["date"], reverse=True)
    return events
