
import pandas as pd
import unicodedata
import numpy as np

def parse_name_to_email(complete_name):

    if complete_name is np.nan or complete_name.strip() == "" or complete_name.lower() == "-": 
        return ""

    return ".".join([normalize_email(i).lower() for i in complete_name.split()]) + "@inheaden.io"

def normalize_email(name):
    """Convert special characters to their ASCII equivalents for email addresses"""
    # Normalize unicode characters (NFD = decompose characters into base + combining marks)
    normalized = unicodedata.normalize('NFD', name)
    # Remove combining marks (accents/diacritics)
    ascii_text = ''.join(char for char in normalized if unicodedata.category(char) != 'Mn')
    return ascii_text

# Function to rename a CSV file
def rename_csv_file(current_path, new_name):
    """
    Rename a CSV file to a new name in the same directory.
    Args:
        current_path (str or Path): The current path to the CSV file.
        new_name (str): The new file name (with .csv extension).
    Returns:
        Path: The new file path after renaming.
    """
    new_path = current_path.with_name(new_name)
    current_path.rename(new_path)
    return new_path

def extract_region_mapping(mapping_file) -> dict:
    region = pd.read_csv(mapping_file)
    region['Name'] = region['Name'].apply(lambda x: x.replace("Inheaden ", ""))
    region_uae = region.loc[region['Name'] == 'UAE', :].to_dict(orient='records')[0]
    
    region_uae['Name'] = "United Arab Emirates"
    
    regions_dict = {region_uae['Name'] : region_uae["Id"]}
    regions_dict.update(dict(zip(region['Name'], region['Id'])))
    return regions_dict