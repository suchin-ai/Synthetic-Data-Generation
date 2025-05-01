import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta, time
from tqdm import tqdm

fake = Faker('en_AU')

# Load Updated Files
logical_df = pd.read_excel(r'B:\Work\Career\HealthCare Logics\Updated_Logical_Artifacts.xlsx')
table_df = pd.read_excel(r'B:\Work\Career\HealthCare Logics\Latest Artifacts.xlsx', sheet_name='Table Artifacts')

# Extract Table Constraints
column_specs = table_df.set_index('column_name').to_dict('index')
from_logical = ['ExtractDate', 'District', 'FacilityDesc', 'SpecialtyName', 'SubSpecialtyName', 'DoctorName', 'ProcedureType', 'Category', 'Age']

mappings = {
    'DoctorName': {}, 'SpecialtyName': {}, 'SubSpecialtyName': {}, 'FacilityDesc': {},
    'PrimaryProcedureDesc': {}, 'PrimaryProcedureCode': {}, 'AccommodationDesc': {},
    'CurrentStatus': {}, 'Unit': {}, 'NRFCReason': {}, 'NRFSComment': {}
}

accommodation_options = {'P': 'Private', 'SP': 'Shared Private', 'W': 'Ward'}
procedure_type_map = {
    'Surgery': ['Appendectomy', 'Cholecystectomy', 'Hip Replacement'],
    'Reconstructive': ['Skin graft', 'Breast reconstruction', 'Cleft palate repair'],
    'Diagnostic': ['Colonoscopy', 'MRI Brain Scan', 'CT Chest'],
    'Preventive': ['Vaccination', 'Routine check-up', 'Dental cleaning']
}
nrfc_reasons = [
    'Awaiting specialist clearance', 'Needs further diagnostic testing', 'Patient request for delay',
    'Pending insurance approval', 'Awaiting rehab scheduling'
]
nrfs_comments = [
    'Pending pre-operative assessment by anesthesia team.',
    'Patient advised to reduce blood pressure before surgery.',
    'Theatre scheduling not confirmed due to equipment shortage.',
    'Awaiting completion of cardiac stress testing.',
    'High INR value — anticoagulant adjustment required.',
    'Infection detected during pre-op screening.',
    'Surgeon not available on planned procedure date.',
    'Need to coordinate with multiple specialties before proceeding.',
    'Final clearance pending from allied health.',
    'Patient requested delay to arrange support post-discharge.'
]
allowed_categories = {'1', '2', '3', '4', '5', '6', '9', 'E', 'NRFC'}

def maybe_null(value, null_pct):
    return None if pd.notna(null_pct) and random.random() < (null_pct / 100.0) else value

def get_or_create_mapping(base, prefix):
    if base not in mappings[prefix]:
        mappings[prefix][base] = f"{prefix[:2].upper()}{random.randint(1000,9999)}"
    return mappings[prefix][base]

records = []
patient_counter = 0

# Loop for Generating Patient Data Row by Row
for _, row in tqdm(logical_df.iterrows(), total=logical_df.shape[0], desc="Generating Patient Records"):
    record_count = int(row['#of Records'])
    for _ in range(record_count):
        gender = random.choice(['Male', 'Female'])
        record = {}
        category = str(row['Category']) if not pd.isna(row['Category']) else 'NRFC'
        if category not in allowed_categories:
            category = 'NRFC'
        for col, spec in column_specs.items():
            null_pct = spec.get('null_percentage', 0) or 0
            dtype = spec.get('data_type')
            format_type = spec.get('DataFormat')
            def maybe(value): return maybe_null(value, null_pct)
            if col in from_logical:
                record[col] = maybe(row[col])
            elif col == 'PatientID':
                record[col] = maybe(f"P{1000000 + patient_counter}")
            elif col == 'PatientGNames':
                record[col] = maybe(fake.first_name_male() if gender == 'Male' else fake.first_name_female())
            elif col == 'PatientSurname':
                record[col] = maybe(fake.last_name())
            elif col == 'PatientGender':
                record[col] = maybe(gender)
            elif col == 'GenderCode':
                record[col] = maybe(1 if gender == 'Male' else 2)
            elif col == 'PatientDoB':
                age = row['Age']
                if pd.isna(age):
                    record[col] = maybe(None)
                else:
                    dob = datetime.today() - timedelta(days=int(age)*365 + random.randint(0, 364))
                    record[col] = maybe(dob.date())
            elif col == 'PatientSuburb':
                record[col] = maybe(fake.city())
            elif col == 'PatientPostCode':
                record[col] = maybe(fake.postcode())
            elif col in ['PatientPhone', 'PatientHomePhone']:
                record[col] = maybe(fake.phone_number())
            elif col == 'DoctorCode':
                record[col] = maybe(get_or_create_mapping(row['DoctorName'], 'DoctorName'))
            elif col == 'SpecialtyCode':
                record[col] = maybe(get_or_create_mapping(row['SpecialtyName'], 'SpecialtyName'))
            elif col == 'SubSpecialtyCode':
                record[col] = maybe(get_or_create_mapping(row['SubSpecialtyName'], 'SubSpecialtyName'))
            elif col == 'Facility':
                record[col] = maybe(get_or_create_mapping(row['FacilityDesc'], 'FacilityDesc'))
            elif col == 'Unit':
                record[col] = maybe(get_or_create_mapping(row['SubSpecialtyName'], 'Unit'))
            elif col == 'ElectiveID':
                subspec_code = get_or_create_mapping(row['SubSpecialtyName'], 'SubSpecialtyName')
                record[col] = maybe(f"EI-{subspec_code}-{patient_counter:05d}")
            elif col == 'CurrentCat':
                record[col] = maybe(category)
            elif col == 'WaitingDays':
                record[col] = maybe(random.randint(0, 300))
            elif col == 'OperationDate':
                rfc = record.get('SurgeryReadyDate')
                record[col] = maybe((rfc + timedelta(days=random.randint(0, 30))).date() if rfc else datetime.today().date())
            elif col == 'CurrentStatus':
                code = record.get('CurrentStatusCode')
                status_map = {'B': 'Booked', 'C': 'Cancelled', 'W': 'Waiting', 'R': 'Removed'}
                record[col] = maybe(status_map.get(code, 'Unknown'))
            elif col == 'CurrentStatusCode':
                if category == 'NRFC':
                    record[col] = maybe('R')
                elif category in ['E', '1', '2', '3']:
                    record[col] = maybe('B')
                else:
                    record[col] = maybe('W')
            elif col == 'CurrentNRFC':
                record[col] = maybe('Yes' if category == 'NRFC' else 'No')
            elif col == 'ReadyForCareDate':
                record[col] = maybe(datetime.today().date() - timedelta(days=random.randint(10, 100)))
            elif col == 'FutureNRFCDays':
                future_days = random.randint(0, 90) if category == 'NRFC' else 0
                record[col] = maybe(future_days)
            elif col == 'LongWait':
                record[col] = maybe(random.choice(['Yes', 'No']))
            elif col == 'EstimatedLos':
                record[col] = None
            elif col in ['EstProcMins', 'SourceEstProcMin']:
                avg_val = max(0, float(spec.get('avg_value') or 60))
                stddev = max(0, float(spec.get('stddev_value') or 15))
                record[col] = maybe(max(0, int(np.random.normal(avg_val, stddev))))
            elif col == 'NRFCReason':
                record[col] = maybe(random.choice(nrfc_reasons) if category == 'NRFC' else None)
            elif col == 'NRFSComment':
                record[col] = maybe(random.choice(nrfs_comments))
            elif col == 'PrimaryProcedureDesc':
                pt = row['ProcedureType']
                if pt not in mappings['PrimaryProcedureDesc']:
                    mappings['PrimaryProcedureDesc'][pt] = random.choice(procedure_type_map.get(pt, ['General procedure']))
                record[col] = maybe(mappings['PrimaryProcedureDesc'][pt])
            elif col == 'PrimaryProcedureCode':
                ddesc = mappings['PrimaryProcedureDesc'].get(row['ProcedureType'])
                record[col] = maybe(get_or_create_mapping(desc, 'PrimaryProcedureCode'))
            elif col == 'OperationProcedure':
                desc = mappings['PrimaryProcedureDesc'].get(row['ProcedureType'])
                record[col] = maybe(desc)
            elif col in ['AccomodationDesc', 'AccommodationDesc']:
                if random.random() < (null_pct / 100.0):
                    record['AccommodationDesc'] = None
                    record['AccommodationCode'] = None
                else:
                    choice_code, choice_desc = random.choice(list(accommodation_options.items()))
                    record['AccommodationDesc'] = choice_desc
                    record['AccommodationCode'] = choice_code
            elif col in ['AccomodationCode', 'AccommodationCode']:
                desc = record.get('AccommodationDesc')
                match = next((k for k, v in accommodation_options.items() if v == desc), 'W')
                record['AccommodationCode'] = maybe(match)
            elif col == 'BookedBeyondBreach':
                if record.get('CurrentStatus') in ['Booked', 'Waiting']:
                    record[col] = maybe(random.choice(['Yes', 'No']))
                else:
                    record[col] = maybe('No')
            elif col == 'WaitGroup':
                if category == 'NRFC':
                    record[col] = maybe('NRFC Group')
                elif category in ['E', '1', '2', '3']:
                    record[col] = maybe('Short Wait')
                else:
                    record[col] = maybe('Long Wait')
            elif col == 'Comments':
                options = [
                    'Patient contacted, waiting for confirmation.',
                    'Pending follow-up from GP.',
                    'Awaiting blood test report.',
                    'No recent updates. Scheduled for next month.',
                    'Call placed to confirm availability.'
                ]
                record[col] = maybe(random.choice(options))
            elif col == 'TheatreSpecialtyName':
                record[col] = maybe(row['SubSpecialtyName'])
            elif col == 'Outsourcing':
                record[col] = maybe(random.choice(['Yes', 'No']))            
            else:
                if dtype == 'datetime2':
                    base = row.get('ExtractDate', pd.Timestamp.now())
                    record[col] = maybe(base + timedelta(seconds=random.randint(0, 86400)))
                elif dtype in ['int', 'bigint']:
                    avg_val = float(spec['avg_value']) if pd.notna(spec['avg_value']) else 100
                    stddev = float(spec['stddev_value']) if pd.notna(spec['stddev_value']) else 10
                    record[col] = maybe(max(0, int(np.random.normal(avg_val, stddev))))
                elif format_type == 'AlphaNumeric':
                    record[col] = maybe(fake.bothify(text='?' * 8))
                elif format_type == 'Mixed/Other':
                    record[col] = maybe(fake.text(max_nb_chars=25))                             
                else:
                    record[col] = maybe(fake.word())
        records.append(record)
        patient_counter += 1
synthetic_df = pd.DataFrame(records)
synthetic_df.to_excel(r'B:\Work\Career\HealthCare Logics\Synthetic_Patient_Data.xlsx', index=False)
print("Synthetic data generation complete and saved.")