# Medical Patient Record & History System

A simple Python mini-project for keeping medical patient records.

Every patient is saved in their own text file inside `data/patients/`.
A central file called `data/master_index.txt` keeps a short summary of
all patients so that searching and listing is fast.

This project was made using only the Python standard library, so no
extra packages are needed.

## Files in this project

```
main.py       -> the menu and all the input/output
records.py    -> Patient class, validation and record logic
storage.py    -> reading and writing the text files
data/         -> where the patient files are stored
```

## How to run

Open a terminal in this folder and run:

```
python main.py
```

If you are using the virtual environment:

```
.venv/bin/python main.py
```

## Menu options

```
1.  Add new patient
2.  Show all patients
3.  Search patient
4.  View patient record
5.  Add diagnosis
6.  Record vitals
7.  Add treatment
8.  View patient history
9.  Delete patient
10. Rebuild master index
0.  Exit
```

## How the data is stored

Each patient has one file, for example `data/patients/P-000001.txt`.
The file is made of pipe-separated lines:

```
PATIENT|id|name|dob|sex|blood_group|phone|address|allergies|registered
DIAGNOSIS|id|date|condition|severity|notes
VITALS|id|date|temp|hr|systolic|diastolic|rr|spo2|weight|height|glucose|notes
TREATMENT|id|date|type|name|dosage|duration|notes
```

The master index stores one line per patient:

```
patient_id|name|dob|sex|blood_group|phone|diagnoses|vitals|treatments|last_visit|file
```

If the index ever gets out of sync with the patient files, use menu
option 10 to rebuild it.

## Extra features

- Age is calculated from the date of birth.
- BMI is calculated when weight and height are entered.
- Vitals are checked and simple warnings are shown, for example
  fever, high blood pressure, low oxygen or high glucose.
- The history view combines diagnoses, vitals and treatments into
  one timeline.

## Sample data

Three sample patients are already added so the project can be
demonstrated immediately. You can delete them from the menu and add
your own records.
