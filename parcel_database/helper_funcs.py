"""
File of helper functions used in exploratory notebooks, for better tracking purposes
"""
import pandas as pd


def data_dict() -> dict:
    """
    Returns a dictionary of data descriptions for the Holyoke parcel data columns
    """
    return {
        "PCL ID": "The parcel ID string",
        "PCL_ID_Tr": "The parcel ID string trimmed for leading/trialing whitespace",
        "HEAT TYPE": "The type of heating system of the parcel",
        "HEAT_TYPE_Tr": "HEAT TYPE string trimmed for leading/trailing whitepace",
        "HEAT FUEL": "The type of heating fuel",
        "HEAT_FUEL_Tr": "HEAT FUEL string trimmed",
        "Heat_Fuel": "A copy of HEAT_FUEL_Tr",
        "DESC": "A description of the parcel",
        "DECS.1": "A copy of DESC",
        "Building Type": "A simplification of DESC, using a customized mapping",
        "Typology": "A copy of Building Type",
        "Decade Built": "Maps YEAR BLT to a decade",
        "YEAR BLT": "The year built",
        "FLA": "The floor are in square feet (?)",
        "FLA.1": "A copy of FLA",
        "Heat_System": "A mapping of HEAT_TYPE_Tr, based on a customized mapping",
        "Vintage": "A copy of Age Category",
        "Age Category": "Custom mapping of YEAR BLT",
        "USE_CLASS": "Custom mapping of DESC and LUC",
        "Number of Units": "Number of units, based on Typology and KITCHENS as a proxy for units",
        "KITCHENS": "Number of kitchens",
        "Numb": "Empty",
        "StateTrimmed": "Empty",
        "STATE CODE": "Empty",
        "ADJ AREA": "Assuming this is adjusted area of ? in units of ?",
        "TOTAL VAL": "Total property value? Appears to be a sum of BUILD VAL, YARD ITEMS, and LAND VAL",
        "BUILD VAL": "Total building value (?)",
        "YARD ITEMS": "What? Some kind of monetary value",
        "LAND VAL": "Total land value (?)",
        "GRANTOR LAST NAME": "Not sure what a grantor is (previous owner?), but probably not important",
        "GRANTOR LAST NAME (2)": "Same comment as GRANTOR LAST NAME",
        "ARMS Sales": "Not sure; probably not important",
        "ARMS Sales (2)": "Same comment as ARMS Sales",
        "SALES PRICE": "Probably the selling price of the property",
        "Sales Price (2)": "Not sure; probably not important",
        "DATE": "Sales date?",
        "DATE (2)": "Sales date?",
        "BK / PG": "No idea",
        "BK / PG (2)": "No idea",
        "COND": "Condition",
        "COND.1": "Condition, again",
        "GRADE": "Seems also like a condition; it's a letter grade",
        "?CURRENT ASSESSMENT?": "Seems like assessment year",
        "FLOORS": "Floor material type",
        "EXT": "Exterior building material?",
        "WALL": "Wall material",
        "SIDING": "Siding material",
        "ROOF": "Roof type?",
        "ROOF_COVER": "Roof cover material",
        "BSMT AREA": "The basement area, in square feet?",
        "BSMT_ALT_FINISH": "From Mike, appears to be finished basement are, in square feet?",
        "PCT_AIR_CONDITIONED": "Percent of building that is air conditioned? Does it include window units?",
        "Central Vacuum": "Boolean var for presence of a central vacuum in the building?",
        "Solar Hot Water": "Boolean var for presence of a solar water heater",
        "Fireplaces": "Number of fireplaces",
        "Building Conditions": "The condition of the building",
        "FULL BA": "Number of full baths",
        "ROOMS": "Number of rooms",
        "BRS": "Number of bedrooms",
        "BATHS": "Number of all bathrooms?",
        "HALF BATHS": "Number of half baths",
        "ST HT": "Not sure",
        "Number of Buildings (Property Cards) ": "Number of buildings on the parcel (with fun trailing whitespace)",
        "SKETCH AREA": "No idea",
        "ACRES": "Acres of the parcel",
        "?PERMIT? ": "Not sure since it's mostly a blank col",
        "LUC": "Some sort of ID number",
        "TRAFFIC": "Car traffic by the parcel?",
        "UTILITY": "The utility for the parcel? Only entry is NONE or PUBLIC",
        "CENSUS": "The census tract?",
        "ZONING": "The zoning of the lot",
        "OWNER": "Owner last name",
        "OWNER 2": "Owner last name",
        "OWNER 3": "Owner last name",
        "CONDO_UNIT": "Whether or not there's a condo unit?",
        "COMPLEX_NAME": "The complex name?",
        "ST NU": "The street number",
        "ST ALT": "Alternative street number",
        "LOCATION": "Street name",
        "MAILING": "Mailing address (just street number and name)",
        "CITY": "City",
        "ST": "State",
        "ZIP": "Zip code",
        "Property Account Number": "Property account number",
        "NULL and Unnamed": "Lots of null or unnamed cols",
    }

def remove_df_whitespace(df: pd.DataFrame) -> pd.DataFrame:
    """
    Strips leadings and trailing whitespace from all string values in a DataFrame
    """
    return df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

def get_cols_to_keep(df: pd.DataFrame) -> list:
    """
    Returns a list of df column names less any unnamed columns
    """
    return [i for i in df.columns if i.find("Unnamed: ") == -1]

# TODO: Remove after discrepancies resolved
def get_building_type_mapping_overlap() -> dict:
    """
    There is some overlap in the building type mapping file for Holyoke and for Wakefield. The
    overlapping DESC's do not map to the same building type in all instances. This function returns
    the discrepancies.
    """
    return {
        "STORE": {"holyoke": "Retail", "wakefield": "Retail"},
        "COMM BLOCK": {"holyoke": "Warehouse", "wakefield": "Office"},
        "COLONIAL": {"holyoke": "Single Family", "wakefield": "Single Family"},
        "WAREHOUSE": {"holyoke": "Warehouse", "wakefield": "Garage"},
        "RANCH": {"holyoke": "Single Family", "wakefield": "Single Family"},
        "ANTIQUE": {"holyoke": "Single Family", "wakefield": "Single Family"},
        "DORMITORY": {"holyoke": "Large Residential", "wakefield": "Large Residential"},
        "BUNGALOW": {"holyoke": "Single Family", "wakefield": "Small Multifamily"},
        "RESTAURANT": {"holyoke": "restaurant", "wakefield": "restaurant"},
        "FUNERAL HM": {"holyoke": "Retail", "wakefield": "Office"},
        "HOTEL": {"holyoke": "Hotel", "wakefield": "Hotel"},
        "MILL": {"holyoke": "Industrial", "wakefield": "Warehouse"},
        "SPLIT CAPE": {"holyoke": "Single Family", "wakefield": "Single Family"},
        "BOWLING AL": {"holyoke": "Assembly", "wakefield": "Assembly"},
    }

# TODO: Remove after discrepancies resolved
def get_building_type_discrepancies() -> dict:
    """
    Returns dict only of the DESC to building type mappings that have discrepancies b/w Holyoke and
    Wakefield datasets
    """
    return {
        "COMM BLOCK": {"holyoke": "Warehouse", "wakefield": "Office"},
        "WAREHOUSE": {"holyoke": "Warehouse", "wakefield": "Garage"},
        "BUNGALOW": {"holyoke": "Single Family", "wakefield": "Small Multifamily"},
        "FUNERAL HM": {"holyoke": "Retail", "wakefield": "Office"},
        "MILL": {"holyoke": "Industrial", "wakefield": "Warehouse"},
    }