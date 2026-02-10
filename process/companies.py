import pandas as pd
from pathlib import Path

from process import extract_region_mapping

DATA_DIR = Path("data")
RAW_FILE = DATA_DIR / "raw" / "Companies_2026_02_10.csv"
PROCESSED_FILE = DATA_DIR / "processed" / "companies.csv"
DROP_COLUMNS = [
    'Company Id', 'Company Owner.id', 'Company Owner', 'Email', "Phone",
    'Tag', 'Created By.id', 'Created By', 'Modified By.id', 'Modified By', 'Modified Time'
]

RENAMED_COLUMN_DICT = {
    "Company Name": "Name",
    "Website": "Website / Link URL",
    "Created Time": "Creation Date",
    "Last Activity Time": "Last update",
    "Address": "Address / Address 1",
    "Country": "Address / Country",
    }

MAPPING_REGION_FILE = DATA_DIR / "twenty_data" / "inheadenRegion.csv"

REGIONS_DICT = extract_region_mapping(MAPPING_REGION_FILE)

country_mapping = {
    "India": [
        "India",
        "india",
    ],
    "United Arab Emirates": [
        "UAE",
        "United Arab Emirates",
        "Dubai, UAE",
        "Dubai UAE",
        "Dubai, AE",
        "Dubai – UAE",
        "Mauritius, UAE",
        "Abu Dhabi, UAE",
        "Sharjah, UAE",
        "Dubai - UAE",
        "United Arab Emirtes",
        "Dubai"
    ],
    "Germany": [
        "Germany",
        "Deutschland",
        "germany",
        "German",
        "Frankfurt am Main"
    ],
}  # [page:1]




def process_companies(input_path, output_path, drop_columns, renamed_column_dict, regions_dict):
    try:
        df = pd.read_csv(input_path)
        for country, variants in country_mapping.items():
            df.loc[df['Country'].isin(variants), "Country"] = country
        
        df["Company Region / Id"] = df['Country'].map(regions_dict)
        # .apply(lambda x: str(x).title() if x is not None else None)
        df.drop(columns=drop_columns, inplace=True)
        df.rename(columns=renamed_column_dict, inplace=True)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"Processed file saved to {output_path} with shape {df.shape}")
    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    process_companies(RAW_FILE, PROCESSED_FILE, DROP_COLUMNS, RENAMED_COLUMN_DICT, REGIONS_DICT)

