"""
Generates scenario inputs for UtilitySim
"""
import numpy as np
import pandas as pd
from typing import Dict, List


PARCEL_DATA_FILEPATH = "./parcel_database/database/wakefield_final_parcel_data.json"
KITCHEN_RETROFITS_FILEPATH = "./parcel_database/kitchen_retrofits.csv"
SCENARIO_FILEPATH = "./parcel_database/utility_sim_inputs.json"


class ScenarioGenerator:
    """
    Creates scenario inputs from the databases for UtilitySim

    Args:
        sim_start_year (int): The simulation start year
        sim_end_year (int): The simulation end year

    Attributes:
        sim_start_year (int): The simulation start year
        sim_end_year (int): The simulation end year
        parcel_data (pd.DataFrame): A DataFrame of the parcel database
        scenario_data (pd.DataFrame): A DataFrame of all scenario data
    """
    def __init__(self, sim_start_year: int, sim_end_year: int):
        self.sim_start_year: int = sim_start_year
        self.sim_end_year: int = sim_end_year

        self.parcel_data: pd.DataFrame = None
        self.scenario_data: pd.DataFrame = None

    def create_scenario(self, parcel_cols: List[str], retrofit_years: Dict[str, int]) -> None:
        """
        Creates scenario inputs JSON file for UtilitySim, based on retrofit years

        Args:
            parcel_cols (List[str]): List of desired columns from the parcel dataset
            retrofit_years (Dict[str, int]): Dict of kitchen retrofit years, organized by parcel ID

        Returns:
            None
        """
        self.parcel_data = pd.read_json(PARCEL_DATA_FILEPATH).transpose()

        self.get_parcel_data_cols(parcel_cols)
        self.add_kitchen_retrofit_data(retrofit_years)
        self.scenario_data["retrofit_cost"] = self.scenario_data.apply(
            self.apply_retrofit_cost, axis=1
        )

        self.scenario_data.to_json(
            SCENARIO_FILEPATH,
            orient="index"
        )

    def get_parcel_data_cols(self, cols: List[str]) -> None:
        """
        Subset the full parcel dataset only to the required columns

        Args:
            cols (List[str]): List of desired columns from the parcel dataset

        Returns:
            None
        """
        self.scenario_data = self.parcel_data.copy()[cols]

    def add_kitchen_retrofit_data(self, retrofit_years: Dict[str, int]) -> None:
        """
        Adds the kitchen retrofit data to the scenario inputs

        Args:
            retrofit_years (Dict[str, int]): Dict of kitchen retrofit years, organized by parcel ID

        Returns:
            None
        """
        kitchen_retrofit_inputs = pd.Series(
            retrofit_years,
            name="retrofit_year"
        )

        self.scenario_data = pd.merge(
            self.scenario_data,
            kitchen_retrofit_inputs,
            how="right",
            left_index=True,
            right_index=True
        )

        self.scenario_data["gas_stove_ops"] = self.scenario_data.apply(
            self.kitchen_scenario,
            axis=1,
            args=(self.sim_start_year, self.sim_end_year)
        )

    @staticmethod
    def kitchen_scenario(
            _x: pd.Series,
            start_year: int,
            end_year: int
    ):
        """
        Determines the kitchen retrofit year based on the fuel type at the building

        Args:
            _x (pd.Series): A Series subset of the overall DataFrame
            start_year (int): The start year of the simulations
            end_year (int): The end year of the simulations

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

    def apply_retrofit_cost(self, _x: pd.Series) -> float:
        """
        Calculates the kitchen retrofit total cost for a pandas Series

        Args:
            _x (pd.Series): The row of a DataFrame, containing all parcel data

        Returns:
            float: The retrofit cost
        """
        retrofit_year = _x["retrofit_year"]
        is_retrofit = (_x["KITCHENS"] >= 1) and (_x["HEAT FUEL"] == "GAS")

        if is_retrofit:
            return self.calculate_retrofit_cost(retrofit_year)

        return 0

    def calculate_retrofit_cost(self, retrofit_year: int):
        """
        Calculates retrofit cost for gas-to-electric stove. Assumes only one kitchen

        Args:
            retrofit_year (int): The year the kitchen retrofit takes place

        Returns:
            float: The total retrofit cost
        """
        removal_labor_time = 2 # hr
        labor_rate = 50 # 2019$ / hr
        existing_removal_labor = removal_labor_time * labor_rate

        new_stove_price = 900 # 2019$
        misc_supplies_price = 100 # 2019$
        retail_markup = 0.18 # percent
        new_stove_material = (new_stove_price + misc_supplies_price) * (1 + retail_markup)

        installation_labor_time = 2 # hr
        installation_labor = installation_labor_time * labor_rate

        total_labor = existing_removal_labor + installation_labor
        total_material = new_stove_material

        escalator = 0.01 # percent
        escalation_factor = (1 + escalator) ** (retrofit_year - self.sim_start_year)

        return (total_labor + total_material) * escalation_factor


if __name__ == "__main__":
    scen_gen = ScenarioGenerator(2025, 2040)
    scen_gen.create_scenario(
        [
            "ST NU", "LOCATION", "MAILING", "ZONING", "LUC", "DESC", "FLA", "KITCHENS",
            "HEAT TYPE", "HEAT FUEL", "STATE CODE", "YEAR BLT", "Decade Built", "Age Category",
            "Heat System", "Number of Units", "Building Type", "Use Class"
        ],
        {
            "2A-009-0QV": 2025,
            "2A-010-0QW": 2029,
            "2A-011-0QX": 2028,
            "2A-012-0QY": 2031,
            "2A-013-0QZ": 2038,
            "2A-014-47A": 2035,
            "05-084-Q27+": 2032,
            "05-076-QK1": 2027,
            "05-077-QL1": 2032,
        }
    )
