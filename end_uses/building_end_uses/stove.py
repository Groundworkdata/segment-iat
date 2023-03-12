"""
Defines Stove end use
"""
from typing import Dict, List

import numpy as np
import pandas as pd


ENERGY_KEYS = [
    "out.electricity.range_oven.energy_consumption",
    "out.natural_gas.range_oven.energy_consumption",
    "out.propane.range_oven.energy_consumption"
]

RESSTOCK_BASELINE_SCENARIO_ID = 0


class Stove:
    """
    Stove end use

    Args:
        resstock_metadata (dict): Need to include ResStock metadata of inputs so we can check if the
        retrofit stove is gas and we need to convert to propane in the NPA scenario

    Keyword Args:
        ?

    Attributes:
        ?

    Methods:
        ?
    """
    def __init__(
            self,
            energy_source: str,
            resstock_consumptions: Dict[int, pd.DataFrame],
            scenario_mapping: List[Dict],
            scenario: int,
            resstock_metadata: dict,
            **kwargs
    ):
        self._kwargs = kwargs

        self.energy_source: str = energy_source
        self._resstock_consumps: Dict[int, pd.DataFrame] = resstock_consumptions
        self._scenario_mapping: List[Dict] = scenario_mapping
        self._scenario: int = scenario
        self._resstock_metadata = resstock_metadata

        self.baseline_energy_use = None
        self._resstock_retrofit_scenario_id: int = None
        self.retrofit_energy_use = None

    def initialize_end_use(self) -> None:
        """
        Initialize the end use and calculate values
        """
        self.baseline_energy_use = self._get_energy_consump_baseline()
        self._resstock_retrofit_scenario_id = self._get_retrofit_scenario()
        self.retrofit_energy_use = self._get_energy_consump_retrofit()

    def _get_energy_consump_baseline(self) -> pd.DataFrame:
        return self._resstock_consumps[RESSTOCK_BASELINE_SCENARIO_ID][ENERGY_KEYS]

    def _get_retrofit_scenario(self) -> int:
        retrofits = self._scenario_mapping[self._scenario]
        return retrofits.get("range_resstock_scenario")

    def _get_energy_consump_retrofit(self) -> pd.DataFrame:
        retrofit_energies = self._resstock_consumps[self._resstock_retrofit_scenario_id][
            ENERGY_KEYS
        ]

        retrofit_fuel = self._scenario_mapping[self._scenario]["replacement_fuel"]
        resstock_retrofit_range = self._resstock_metadata["in.cooking_range"]

        if "propane" not in resstock_retrofit_range.lower() and retrofit_fuel=="propane":
            retrofit_energies = self._adjust_retrofit_energies(retrofit_energies)

        return retrofit_energies

    @staticmethod
    def _adjust_retrofit_energies(retrofit_energies: pd.DataFrame) -> pd.DataFrame:
        retrofit_energies["out.propane.range_oven.energy_consumption"] += \
            retrofit_energies["out.natural_gas.range_oven.energy_consumption"]
        
        retrofit_energies["out.natural_gas.range_oven.energy_consumption"] = 0

        return retrofit_energies

    #FIXME
    def get_install_cost(self) -> List[float]:
        """
        Calculates installation cost for a stove. Overwrites parent method

        Stove installation cost is as follows:
            (labor removal rate) * (labor time)
            + ((new stove price) + (miscellaneous supplies price)) * (1 + (retail markup percent))
            + (labor installation rate) * (labor time)

        All rates are in today's dollars. Total stove installation cost is multiplied by an annual
        escalation factor to get cost for the corresponding installation year
        """
        removal_labor_time = self._kwargs.get("removal_labor_time") # hr
        labor_rate = self._kwargs.get("labor_rate") # $ / hr
        existing_removal_labor = removal_labor_time * labor_rate

        misc_supplies_price = self._kwargs.get("misc_supplies_price") # $
        retail_markup = self._kwargs.get("retail_markup") # percent
        new_stove_material = (self.asset_cost + misc_supplies_price) * (1 + retail_markup)

        installation_labor_time = self._kwargs.get("installation_labor_time") # hr
        installation_labor = installation_labor_time * labor_rate

        total_labor = existing_removal_labor + installation_labor
        total_material = new_stove_material

        escalator = self._kwargs.get("annual_cost_escalation") # percent
        escalation_factor = (1 + escalator) ** (self.install_year - self.sim_start_year)

        total_cost = (total_labor + total_material) * escalation_factor
        total_cost = round(total_cost, 2)

        install_cost = np.zeros(len(self.operational_vector)).tolist()
        # If the install is outside of the sim years, then we ignore the install cost
        if self.sim_start_year <= self.install_year <= self.sim_end_year:
            install_cost[self.install_year - self.sim_start_year] = total_cost

        return install_cost
