"""
Creates enriched parcel database based on cleaned raw data
"""
import pandas as pd
import numpy as np


YEAR_BUILT_LABEL = "YEAR BLT"
HEAT_TYPE_LABEL = "HEAT TYPE"
FLOOR_AREA_LABEL = "FLA"
NUM_KITCHENS_LABEL = "KITCHENS"


# TODO: Check some of the database cleaning... ZIP code in Wakefield in 01880, but leading 0 has
# been removed, probably through a Python way of handling this value as an int


def create_decade_built_data(db_df: pd.DataFrame) -> pd.Series:
    """
    Create a column for the database that gives the decade the building was built

    Args:
        db_df (pd.DataFrame): DataFrame of the database

    Return:
        pd.Series: Series of decade built
    """
    return (
        (db_df[YEAR_BUILT_LABEL].fillna(0) // 10) * 10
    ).astype(int).replace(0, np.nan)

def _age_category_mapping(_x: pd.Series) -> str:
    """
    Maps year built to an age category string

    Args:
        _x (pd.Series): A row of the database

    Return:
        str: The age category string
    """
    year = _x[YEAR_BUILT_LABEL]

    if pd.isnull(year):
        return "POST2000"

    else:
        if year < 1950:
            return "PRE1950"
        elif year >= 1950 and year < 1980:
            return "1950 - 1979"
        elif year >= 1980 and year < 2000:
            return "1980 - 1999"

    return "POST2000"

def create_age_category_data(db_df: pd.DataFrame) -> pd.Series:
    """
    Create a column for the database that gives the age category

    Args:
        db_df (pd.DataFrame): DataFrame of the database

    Return:
        pd.Series: Series of age category
    """
    return db_df.apply(_age_category_mapping, axis=1)

def _heat_system_mapping(_x: pd.Series) -> str:
    """
    Maps heat type to a heat system string

    Args:
        _x (pd.Series): A row of the database

    Return:
        str: The heat system string
    """
    mapping = {
        None: None,
        "STEAM": "STEAM",
        "FORCED H/A": "DUCTED",
        "FORCED H/W": "NON-DUCTED",
        "UNIT HTRS": "NON-DUCTED",
        "ELECTRC BB": "NON-DUCTED",
        "RADIANT HW": "NON-DUCTED",
        "GRAVTY H/A": "NON-DUCTED",
        "FLOOR FURN": "NON-DUCTED",
        "NOT DUCTED": "NON-DUCTED",
        "AVERAGE": "NON-DUCTED",
        "WALL UNIT": "NON-DUCTED",
    }

    return mapping.get(_x[HEAT_TYPE_LABEL])

def create_heat_system_data(db_df: pd.DataFrame) -> pd.Series:
    """
    Create a column for the database that gives the heat system

    Args:
        db_df (pd.DataFrame): DataFrame of the database

    Return:
        pd.Series: Series of the heat system
    """
    return db_df.apply(_heat_system_mapping, axis=1)

def _number_of_units_mapping(_x: pd.Series) -> int:
    floor_area = _x[FLOOR_AREA_LABEL]
    num_kitchens = _x[NUM_KITCHENS_LABEL]

    if num_kitchens > 0 and floor_area > 0:
        return num_kitchens
    return 0

def create_number_of_units_data(db_df: pd.DataFrame) -> pd.Series:
    return db_df.apply(_number_of_units_mapping, axis=1)

def set_building_type(_x, mapping_dict) -> str:
    return mapping_dict.get(_x["DESC"])

def create_building_type_data(db_df: pd.DataFrame) -> pd.Series:
    building_type_map_filepath = "./parcel_database/database/mappings/full_building_type_mappings.csv"
    full_mapping = pd.read_csv(building_type_map_filepath).set_index("DESC")
    full_mapping = full_mapping.to_dict()["Building Type"]

    return db_df.apply(set_building_type, axis=1, args=(full_mapping,))

def _map_use_class(_x, mapping):
    label = str(_x["LUC"]) + ' - ' + str(_x["DESC"])
    return mapping.get(label)

def _map_use_class_wakefield(_x, mapping):
    label = str(_x["DESC"])
    return mapping.get(label)

def create_use_class_data(db_df: pd.DataFrame, city: str) -> pd.Series:
    if city == "WAKEFIELD":
        filepath = "./parcel_database/database/mappings/map_wakefield_UseClass.csv"
        mapping_func = _map_use_class_wakefield
        map_df = pd.read_csv(filepath)

        mapping_dict = map_df.set_index("DESC").to_dict()["Classification"]

    else:
        filepath = "./parcel_database/database/mappings/map_LUCandDESC_UseClass.csv"
        mapping_func = _map_use_class

        map_df = pd.read_csv(filepath)
        mapping_dict = map_df[[
            "USE_CLASS", "mapping_label"
        ]].set_index("mapping_label").to_dict()["USE_CLASS"]

    # Hacky way to handle any NaNs in the df
    return db_df.fillna('').apply(mapping_func, axis=1, args=(mapping_dict,))


def main():
    # FILEPATH = "./parcel_database/database/raw_parcel_data/raw_parcel_data.csv"
    # CITY = "HOLYOKE"
    FILEPATH = "./parcel_database/database/raw_parcel_data/parcel_wakefield_raw_cleaned.csv"
    CITY = "WAKEFIELD"
    df = pd.read_csv(FILEPATH)

    df["Decade Built"] = create_decade_built_data(df)
    df["Age Category"] = create_age_category_data(df)
    df["Heat System"] = create_heat_system_data(df)
    df["Number of Units"] = create_number_of_units_data(df)
    df["Building Type"] = create_building_type_data(df)
    df["Use Class"] = create_use_class_data(df, CITY)

    # OUTPUT_FILEPATH = "./parcel_database/database/holyoke_final_parcel_data.csv"
    OUTPUT_FILEPATH_CSV = "./parcel_database/database/wakefield_final_parcel_data.csv"
    df.to_csv(OUTPUT_FILEPATH_CSV, index=False)

    OUTPUT_FILEPATH_JSON = "./parcel_database/database/wakefield_final_parcel_data.json"
    df.set_index("PCL ID").to_json(OUTPUT_FILEPATH_JSON, orient="index")

if __name__ == "__main__":
    main()
