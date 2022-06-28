"""
Generates scenario inputs for model
"""
import numpy as np
import pandas as pd

PARCEL_DATA_FILEPATH = "./parcel_database/data_explore/parcel_data/json_db_prototype.json"
KITCHEN_RETROFIT_YEARS_FILEPATH = \
    "./parcel_database/data_explore/utility_sim/kitchen_retrofit_seed.csv"

def main(start_year: int, end_year: int):
    """
    Reads in parcel data and creates scenario data for simulation purposes. Scenario data written to
        kitchen_scenario_inputs.json file

    Args:
        start_year (int): The simulation start year
        end_year (int): The simulation end year (exclusive)

    Returns:
        None
    """
    df = pd.read_json(PARCEL_DATA_FILEPATH).transpose()
    print(df)


    kitchen_retrofit_inputs = pd.read_csv(KITCHEN_RETROFIT_YEARS_FILEPATH).set_index("PCL_ID")
    print(kitchen_retrofit_inputs)

    merged_df = pd.merge(
        df,
        kitchen_retrofit_inputs,
        how="right",
        left_index=True,
        right_index=True
    )
    print(merged_df)

    merged_df["gas_stove_ops"] = merged_df.apply(
        kitchen_scenario,
        axis=1,
        args=(start_year, end_year)
    )

    print(merged_df)

    merged_df.to_json(
        "./parcel_database/data_explore/utility_sim/sim_inputs_prototype.json",
        orient="index"
    )


def kitchen_scenario(
        _x: pd.Series,
        start_year: int,
        end_year: int
):
    """
    Determines the kitchen retrofit year based on the fuel type at the building

    Args:
        kitchen_retrofit_year (int): The kitchen retrofit year

    Returns:
        Optional[int]: The kitchen retrofit year, if applicable; otherwise None
    """
    kitchen_retrofit_yr = _x["retrofit_year"]

    if _x["KITCHENS"] < 1:
        kitchen_retrofit_yr = start_year

    if _x["HEAT FUEL"] != "GAS":
        kitchen_retrofit_yr = start_year

    gas_stove_ops = np.concatenate((
        np.ones(kitchen_retrofit_yr-start_year, dtype=int),
        np.zeros(end_year-kitchen_retrofit_yr, dtype=int)
    ))

    return gas_stove_ops


if __name__ == "__main__":
    main(2025, 2040)
