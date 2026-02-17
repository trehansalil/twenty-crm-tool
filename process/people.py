
"""
People Data Processing Module

This module processes contact data from raw CSV files, applies transformations,
and generates cleaned data for import into the Twenty CRM system.
"""

import logging
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd

from process import extract_region_mapping_new, format_array_fields, map_company_ids, parse_name_to_email, parse_phone_json, save_processed_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Directory paths
DATA_DIR = Path("data")
RAW_FILE = DATA_DIR / "raw" / "Contacts_2026_02_12.csv"
PROCESSED_FILE = DATA_DIR / "processed" / "peoples.csv"
ISSUES_FILE = DATA_DIR / "issues" / "people_issues.csv"
COMPANY_TWENTY_FILE = DATA_DIR / "twenty_data" / "company.csv"
MAPPING_REGION_FILE = DATA_DIR / "twenty_data" / "inheadenRegion.csv"

# Load region mappings
REGIONS_DICT = extract_region_mapping_new(MAPPING_REGION_FILE)

# Columns to remove from raw data
DROP_COLUMNS: List[str] = [
    'Contact Id',
    'Contact Owner.id',
    'Contact Name',
    'Created By.id',
    'Created By',
    'Modified By.id',
    'Modified By',
    'Modified Time',
    'Company Name.id',
    'Secondary Email',
    'Company Name',
    'Unsubscribed Mode',
    'Unsubscribed Time',
    'Data Source'
]

# Column name mappings for CRM import format
RENAMED_COLUMNS: Dict[str, str] = {
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

# Email addresses for user consolidation
ADMIN_EMAIL = 'admin@inheaden.io'

DEPRECATED_USER_EMAILS = [
    'traudel.boakye@inheaden.io',
    'ahmed.elshamanhory@inheaden.io',
    'inheaden.admin@inheaden.io'
]

UNREGISTERED_USER_EMAILS = [
    # 'florian.schlichting@inheaden.io',
    'sabine.schafer@inheaden.io',
    # 'jeanette.natalie@inheaden.io'
]

USER_EMAIL_CORRECTIONS = {
    'lars.grober@inheaden.io': 'lars.groeber@inheaden.io'
}

# Title standardization mapping
TITLE_MAPPING: Dict[str, str] = {
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

# Country to region mapping for CRM
COUNTRY_REGION_MAPPING: Dict[str, List[str]] = {
    "Inheaden Europe": [
        "Germany",
        "Belgium",
        "Czech Rep.",
        "Denmark",
        "Estonia",
        "Finland",
        "Sweden",
        "England",
        "Switzerland",
        "Poland",
        "Austria",
        "UK",
        "Costa Rica",
        "Vanuatu",
        "Italy",
        "Portugal",
        "Deutschland",
        "Germany, English",
        "Germany."
    ],
    "Inheaden India": [
        "India",
        "india"
    ],
    "Inheaden Middle East": [
        "UAE",
        "Kuwait",
        "Lebanon",
        "Egypt",
        "Saudi Arabia",
        "Mauritius, UAE",
        "Abu Dhabi, UAE",
        "Sharjah, UAE",
        "United Arab Emirates",
        "Dubai",
        "Oman",
        "Bahrain",
        "KSA",
        "united arab emirates"
    ]
}


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load raw contact data and company reference data.
    
    Returns:
        tuple: A tuple containing (contacts_df, companies_df)
        
    Raises:
        FileNotFoundError: If required data files are not found
    """
    logger.info(f"Loading contact data from {RAW_FILE}")
    contacts_df = pd.read_csv(RAW_FILE)
    
    logger.info(f"Loading company data from {COMPANY_TWENTY_FILE}")
    companies_df = pd.read_csv(COMPANY_TWENTY_FILE)
    
    return contacts_df, companies_df


def normalize_contact_owners(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize and correct contact owner email addresses.
    
    Args:
        df: DataFrame containing contact data
        
    Returns:
        pd.DataFrame: DataFrame with normalized contact owner emails
    """
    logger.info("Normalizing contact owner emails")
    
    # Parse names to email format
    df['Contact Owner'] = df['Contact Owner'].map(parse_name_to_email)
    
    # Consolidate deprecated user emails to admin
    df.loc[df['Contact Owner'].isin(DEPRECATED_USER_EMAILS), 'Contact Owner'] = ADMIN_EMAIL
    
    # Apply email corrections
    for old_email, new_email in USER_EMAIL_CORRECTIONS.items():
        df.loc[df['Contact Owner'] == old_email, 'Contact Owner'] = new_email
    
    # Handle unregistered users
    df.loc[df['Contact Owner'].isin(UNREGISTERED_USER_EMAILS), 'Contact Owner'] = ADMIN_EMAIL
    
    return df


def normalize_titles(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize title values according to mapping.
    
    Args:
        df: DataFrame containing contact data
        
    Returns:
        pd.DataFrame: DataFrame with normalized titles
    """
    logger.info("Normalizing contact titles")
    df["Title"] = df['Title'].map(TITLE_MAPPING)
    return df


def assign_regions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Assign region IDs based on country values.
    
    Args:
        df: DataFrame containing contact data
        
    Returns:
        pd.DataFrame: DataFrame with region IDs assigned
    """
    logger.info("Assigning regions based on countries")
    
    for region, countries in COUNTRY_REGION_MAPPING.items():
        df.loc[df['Country'].isin(countries), 'Contact Region / Id'] = REGIONS_DICT[region]
    
    return df


def transform_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply final transformations: drop unnecessary columns and rename fields.
    
    Args:
        df: DataFrame containing contact data
        
    Returns:
        pd.DataFrame: Transformed DataFrame ready for export
    """
    logger.info("Applying final transformations")
    
    df = df.drop(columns=DROP_COLUMNS)
    df = df.rename(columns=RENAMED_COLUMNS)
    
    return df


def process_people_data() -> None:
    """
    Main processing pipeline for contact data.
    
    This function orchestrates the complete data processing workflow:
    1. Load raw data
    2. Normalize contact owners and titles
    3. Map company IDs
    4. Format array fields
    5. Assign regions
    6. Transform and save final data
    """
    try:
        # Load data
        df, companies_df = load_data()
        logger.info(f"Loaded {len(df)} contact records")
        
        # Apply transformations
        df = normalize_contact_owners(df)
        df = normalize_titles(df)
        df = map_company_ids(df, companies_df)
        df = format_array_fields(df)
        df = assign_regions(df)
        df = transform_dataframe(df)
        
        # Save results
        save_processed_data(df, PROCESSED_FILE)
        
        logger.info("People data processing completed successfully")
        
    except FileNotFoundError as e:
        logger.error(f"Required file not found: {e}")
        raise
    except Exception as e:
        logger.error(f"Error processing people data: {e}")
        raise


if __name__ == "__main__":
    process_people_data()