import random
from faker import Faker

# Initialize faker
fake = Faker()

# --- Step 1: Generate Specialty Names ---

# Some real-world medical specialties
specialties = [
    "Cardiology", "Neurology", "Orthopedics", "Dermatology", "Pediatrics",
    "Oncology", "Gastroenterology", "Psychiatry", "Endocrinology", "Ophthalmology",
    "Rheumatology", "Pulmonology", "Nephrology", "Hematology", "Infectious Disease",
    "Allergy and Immunology", "Anesthesiology", "General Surgery", "Plastic Surgery",
    "Vascular Surgery", "Emergency Medicine", "Internal Medicine", "Family Medicine",
    "Geriatrics", "Obstetrics and Gynecology", "Pathology", "Radiology", "Urology",
    "Otolaryngology", "Palliative Care", "Sports Medicine", "Pain Management",
    "Rehabilitation Medicine", "Genetics", "Occupational Medicine"
]

# Pick 35 specialties
selected_specialties = random.sample(specialties, 35)

# --- Step 2: Generate Sub-Specialty Names (Improved) ---

# Base subspecialty templates
subspecialty_templates = [
    "Pediatric {}", "Geriatric {}", "Interventional {}", "Surgical {}",
    "Diagnostic {}", "Clinical {}", "Advanced {}", "Acute Care {}", "Preventive {}",
    "Emergency {}", "Reconstructive {}"
]

selected_subspecialties = []
attempts = 0

while len(selected_subspecialties) < 55:
    specialty = random.choice(selected_specialties)
    other_specialty = random.choice(selected_specialties)

    # Make sure specialty and other_specialty are different
    if specialty != other_specialty:
        template = random.choice(subspecialty_templates)
        subspecialty = template.format(other_specialty)

        # Also avoid duplicates
        if subspecialty not in selected_subspecialties:
            selected_subspecialties.append(subspecialty)
    else:
        # If same, skip and retry
        attempts += 1
        if attempts > 500:  # Safety break
            break


# Generate 55 sub-specialties by randomly combining
selected_subspecialties = []
while len(selected_subspecialties) < 55:
    specialty = random.choice(selected_specialties)
    template = random.choice(subspecialty_templates)
    subspecialty = template.format(specialty)
    if subspecialty not in selected_subspecialties:
        selected_subspecialties.append(subspecialty)

# --- Step 3: Generate Doctor Names ---

doctor_names = []
for _ in range(288):
    name = f"Dr. {fake.first_name()} {fake.last_name()}"
    doctor_names.append(name)

# --- Display the generated names ---

print("\n=== Specialty Names (35) ===")
for s in selected_specialties:
    print(s)

print("\n=== Sub-Specialty Names (55) ===")
for ss in selected_subspecialties:
    print(ss)

print("\n=== Doctor Names (288) ===")
for d in doctor_names:
    print(d)

# --- Optionally, save to CSV ---
import pandas as pd

# Save to CSV if you want
df_specialties = pd.DataFrame(selected_specialties, columns=["SpecialtyName"])
df_subspecialties = pd.DataFrame(selected_subspecialties, columns=["SubSpecialtyName"])
df_doctors = pd.DataFrame(doctor_names, columns=["DoctorName"])
save_path = r"b:\Work\Career\HealthCare Logics\Generated_Names.xlsx"
with pd.ExcelWriter(save_path) as writer:
    df_specialties.to_excel(writer, sheet_name="Specialties", index=False)
    df_subspecialties.to_excel(writer, sheet_name="SubSpecialties", index=False)
    df_doctors.to_excel(writer, sheet_name="Doctors", index=False)
print("\nNames saved to 'Generated_Names.xlsx'")
