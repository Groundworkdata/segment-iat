"""
Helper function for grabbing building data directly from ResStock
"""
import pandas as pd

def resstock_connector(state: str, scenario: int, building_id: int) -> pd.DataFrame:
    """
    ResStock connection for the 2022 release 1.1

    Args:
        state (str): The state code
        scenario (int): The simulation scenario
        building_id (int): The ID of the individual building
    """
    BUILDING_BASE_URL = "https://oedi-data-lake.s3.amazonaws.com/"\
                "nrel-pds-building-stock/end-use-load-profiles-for-us-building-stock/2022/"\
                "resstock_amy2018_release_1.1/timeseries_individual_buildings/by_state/"

    building_url = BUILDING_BASE_URL + "upgrade={0}/state={1}/{2}-{0}.parquet".format(
        scenario, state, building_id
    )

    response = pd.read_parquet(building_url)

    return response
