
import numpy as np
import pandas as pd
from pathlib import Path

from process import parse_name_to_email, parse_phone_json

DATA_DIR = Path("data")

RAW_FILE = DATA_DIR / "raw" / "Contacts_2026_02_12.csv"

PROCESSED_FILE = DATA_DIR / "processed" / "peoples.csv"

ISSUES_FILE = DATA_DIR / "issues" / "people_issues.csv"

COMPANY_TWENTY_FILE = DATA_DIR / "twenty_data" / "company.csv"

DROP_COLUMNS = [
    'Contact Id', 'Contact Owner.id', "Contact Name", 'Created By.id', 'Created By', 'Modified By.id', 'Modified By', 'Modified Time', 
    "Company Name.id", "Secondary Email", "Company Name", 'Unsubscribed Mode', 'Unsubscribed Time', 'Data Source'
]

RENAMED_COLUMNS = {
    # 'Contact Id': 'Id',
    "First Name": 'Name / First Name',
    "Last Name": 'Name / Last Name',
    'Contact Owner': 'Contact Owner / User Email',
    "Position": "Job Title",
    "Email": "Emails / Primary Email",
    "Private Email": "Emails / Additional Emails",
    "Phone": "Phones / Primary Phone",
    "Home Phone": "Phones / Additional Phones",
    "Tag": "Tags",
    "Social Media": "Linkedin / Link URL",
    "Created Time": "Creation Date",
    "Mobile": "Mobile / Primary Phone Number",
    "Last Activity Time": "Last Update",
    "Address": "Address / Address 1",
    "Country": "Address / Country",
    "Primary Language Spoken": "Primary Language",
    "Secondary Language Spoken": "Secondary Language",    
}

title_mapping = {
    'nan': np.nan,
    'Business Administrator': np.nan,
    'Dr.': 'Dr.',
    'Dipl.-Wirtsch.-Ing. (TU)': np.nan,
    'CEO': np.nan,
    'CDO': np.nan,
    'CIO': np.nan,
    'DevOps Developer': np.nan,
    'CTO': np.nan,
    'Head of Marketing': np.nan,
    'Dr': 'Dr.',
    'Prof. Dr.': 'Prof.',
    'Dr.-Ing.': 'Dr.',
    'Start a Project': np.nan,
    'Career': np.nan,
    'Dipl.- Wirtschafts.Ing.': np.nan,
    'Prof. Dr. Dr. h.c. mult.': 'Prof.',
    'Dr. jur.': 'Dr.',
    'Dipl.-Ing.': np.nan,
    'Mr': 'Mr.',
    'Frontend Developer': np.nan,
    'Head of Legal': np.nan,
    'React Developer': np.nan,
    'Designer': np.nan,
    'Head of Operations India': np.nan,
    'QA Engineer': np.nan,
    'Finance Manager': np.nan,
    'Ms': 'Ms.',
    'Prof. Dr. med.': 'Prof.',
    'Prof.Dr.': 'Prof.',
    'Prof. Dr. Dr. Habil.': 'Prof.',
    'Junior Designer': np.nan,
    'Intern': np.nan,
    'Software Intern': np.nan,
    'Junior DevOps Engineer': np.nan,
    'Project Manager': np.nan,
    'Fullstack Developer': np.nan,
    'Product Designer': np.nan,
    'Marketing Designer': np.nan,
    'Executive Assistant': np.nan,
    'UAE MoHRE Project': np.nan,
    'Tech Angel': np.nan,
    'Data Scientist': np.nan,
    'DevOps Engineer': np.nan,
    'UX/UI Designer': np.nan,
    'Backend Developer': np.nan,
    'Marketing Intern': np.nan,
    'Golang Developer': np.nan,
    'Lawyer (Hamburg)': np.nan,
    'Creater, Winemaker & Founder': np.nan,
    'Dipl-Ing.Architekt': np.nan,
    'M.Sc.': np.nan,
    'M.A.': np.nan,
    'Dr. med.': 'Dr.',
    'Solution Specialist & Business Developer': np.nan,
    'Digital Transformation Expert - Business Analyst - Design Thinking': np.nan,
    'PhD': np.nan
}


df = pd.read_csv(RAW_FILE)

companies_df = pd.read_csv(COMPANY_TWENTY_FILE)

df['Contact Owner'] = df['Contact Owner'].map(parse_name_to_email)
df.loc[df['Contact Owner'].isin(['traudel.boakye@inheaden.io',
'ahmed.elshamanhory@inheaden.io', 'inheaden.admin@inheaden.io']), 'Contact Owner'] = 'admin@inheaden.io'
company_name_id_mapping = dict(zip(companies_df['Name'], companies_df['Id']))
df["Title"] = df['Title'].map(title_mapping)

df['Company Id'] = df['Company Name'].map(lambda x: company_name_id_mapping.get(x, x))
df['Tag'] = df['Tag'].astype(str).apply(lambda x: '[]' if x == 'nan' else (f'["{x}"]' if len(x.split())>0 else '[]'))

df['Home Phone'] = df['Home Phone'].astype(str).apply(parse_phone_json)
df['Private Email'] = df['Private Email'].astype(str).apply(lambda x: '[]' if x == 'nan' else (f'["{x}"]' if len(x.split())>0 else '[]'))

df.drop(columns=DROP_COLUMNS, inplace=True)
df.rename(columns=RENAMED_COLUMNS, inplace=True)
df.head()
PROCESSED_FILE.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(PROCESSED_FILE, index=False)