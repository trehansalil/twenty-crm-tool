
import pandas as pd


def extract_region_mapping(mapping_file) -> dict:
    region = pd.read_csv(mapping_file)
    region['Name'] = region['Name'].apply(lambda x: x.replace("Inheaden ", ""))
    region_uae = region.loc[region['Name'] == 'UAE', :].to_dict(orient='records')[0]
    
    region_uae['Name'] = "United Arab Emirates"
    
    regions_dict = {region_uae['Name'] : region_uae["Id"]}
    regions_dict.update(dict(zip(region['Name'], region['Id'])))
    return regions_dict