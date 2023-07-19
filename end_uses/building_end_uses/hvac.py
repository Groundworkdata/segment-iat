"""
Defines HVAC end use
"""
from typing import Dict, List

import numpy as np
import pandas as pd


ENERGY_KEYS = [
    "out.electricity.heating.energy_consumption",
    "out.electricity.heating_hp_bkup.energy_consumption", # hybrid configuration
    "out.electricity.cooling.energy_consumption",
    "out.natural_gas.heating.energy_consumption",
    "out.natural_gas.heating_hp_bkup.energy_consumption", # hybrid configuration
    "out.propane.heating.energy_consumption",
    "out.propane.heating_hp_bkup.energy_consumption", # hybrid configuration
    "out.fuel_oil.heating.energy_consumption",
    "out.fuel_oil.heating_hp_bkup.energy_consumption", #hybrid configuration
]

RESSTOCK_BASELINE_SCENARIO_ID = 0

INFLATION_ESCALATOR = 0.02


class HVAC:
    """
    HVAC end use

    Args:
        energy_source (str): The energy source of the baseline asset
        resstock_consumptions (Dict[int, pd.DataFrame]): Dict of energy consumption timeseries
            organized by retrofit scenario
        scenario_mapping (List[Dict]): Mapping of ResStock scenarios to Groundwork scenarios
        scenario (int): The retrofit intervention scenario
        resstock_metadata (dict): Dict of metadata from ResStock
        years_vec (List[int]): List of simulation years

    Optional Args:
        custom_baseline_energy (pd.DataFrame): Custom input timeseries of baseline energy consump
        custom_retrofit_energy (pd.DataFrame): Custom input timeseries of retrofit energy consump

    Keyword Args:
        existing_install_year (int): Install year of the baseline asset
        lifetime (int): Useful lifetime of the asset in years
        replacement_cost_dollars_year (int): Reference year for the input costs
        escalator (float): Inflation escalator for cost calculations
        existing_install_cost (float): Installation cost of the baseline asset
        replacement_year (int): Year of retrofit
        replacement_cost (float): Cost of replacing asset
        replacement_lifetime (int): Useful lifetime of the replacement asset in years
        end_use (str): The asset type

    Attributes:
        existing_book_val (List[float]): The annual book value of the existing asset
        replacement_cost (List[float]): The annual cost of asset replacement
        replacement_book_val (List[float]): The annual book value of the replacement asset
        cost_table (pd.DataFrame): Table of annual costs for the asset
        baseline_energy_use (pd.DataFrame): Timeseries baseline energy consumption for a full year
        retrofit_energy_use (pd.DataFrame): Timeseries retrofit energy consumption for a full year

    Methods:
        initialize_end_use (None): Calculate all associated asset values
    """
    def __init__(
            self,
            energy_source: str,
            resstock_consumptions: Dict[int, pd.DataFrame],
            scenario_mapping: List[Dict],
            scenario: int,
            resstock_metadata: dict,
            years_vec: List[int],
            custom_baseline_energy: pd.DataFrame = pd.DataFrame(),
            custom_retrofit_energy: pd.DataFrame = pd.DataFrame(),
            **kwargs
    ):
        self._kwargs = kwargs

        self._energy_source: str = energy_source
        self._resstock_consumps: Dict[int, pd.DataFrame] = resstock_consumptions
        self._scenario_mapping: List[Dict] = scenario_mapping
        self._scenario: int = scenario
        self._resstock_metadata = resstock_metadata
        self._years_vec: List[int] = years_vec
        self._custom_baseline_energy: pd.DataFrame = custom_baseline_energy
        self._custom_retrofit_energy: pd.DataFrame = custom_retrofit_energy

        self.existing_book_val: List[float] = []
        self._replacement_vec: List[bool] = []
        self.replacement_cost: List[float] = []
        self.replacement_book_val: List[float] = []
        self.cost_table: pd.DataFrame = None

        self.baseline_energy_use = None
        self._resstock_retrofit_scenario_id: int = None
        self.retrofit_energy_use = None

    def initialize_end_use(self) -> None:
        """
        Initialize the end use and calculate values
        """
        self.existing_book_val = self._get_existing_book_val()
        self._replacement_vec = self._get_replacement_vec()
        self.existing_stranded_val = self._get_existing_stranded_val()
        self.replacement_cost = self._get_replacement_cost()
        self.replacement_book_val = self._get_replacement_book_value()
        self.cost_table = self._get_cost_table()

        if not self._custom_baseline_energy.empty and not self._custom_retrofit_energy.empty:
            self._get_custom_energies()

        else:
            self.baseline_energy_use = self._get_energy_consump_baseline()
            self._resstock_retrofit_scenario_id = self._get_retrofit_scenario()
            self.retrofit_energy_use = self._get_energy_consump_retrofit()

    def _get_custom_energies(self) -> None:
        self.baseline_energy_use = self._custom_baseline_energy.reindex(
            ENERGY_KEYS, axis=1, fill_value=0
        )

        self.retrofit_energy_use = self._custom_retrofit_energy.reindex(
            ENERGY_KEYS, axis=1, fill_value=0
        )

    def _get_energy_consump_baseline(self) -> pd.DataFrame:
        return self._resstock_consumps[RESSTOCK_BASELINE_SCENARIO_ID][ENERGY_KEYS]

    def _get_retrofit_scenario(self) -> int:
        retrofits = self._scenario_mapping[self._scenario]
        return retrofits.get("hvac_resstock_scenario")

    def _get_energy_consump_retrofit(self) -> pd.DataFrame:
        retrofit_energies = self._resstock_consumps[self._resstock_retrofit_scenario_id][
            ENERGY_KEYS
        ]

        retrofit_fuel = self._scenario_mapping[self._scenario]["replacement_fuel"]
        # Main heating fuel from baseline scenario
        # This will also tell us the backup heating fuel in hybrid scenarios
        resstock_retrofit_heating_fuel = self._resstock_metadata["in.heating_fuel"]

        if "propane" not in resstock_retrofit_heating_fuel.lower() and retrofit_fuel=="propane":
            retrofit_energies = self._adjust_retrofit_energies(retrofit_energies)

        return retrofit_energies

    @staticmethod
    def _adjust_retrofit_energies(retrofit_energies: pd.DataFrame) -> pd.DataFrame:
        retrofit_energies["out.propane.heating.energy_consumption"] += \
            retrofit_energies["out.natural_gas.heating.energy_consumption"]
        
        retrofit_energies["out.propane.heating_hp_bkup.energy_consumption"] += \
            retrofit_energies["out.natural_gas.heating_hp_bkup.energy_consumption"]

        retrofit_energies["out.natural_gas.heating.energy_consumption"] = 0
        retrofit_energies["out.natural_gas.heating_hp_bkup.energy_consumption"] = 0

        return retrofit_energies

    def _get_existing_book_val(self) -> List[float]:
        existing_install_year = self._kwargs.get("existing_install_year", self._years_vec[0])
        lifetime = self._kwargs.get("lifetime", 10)
        existing_cost_dollars_year = self._kwargs.get("replacement_cost_dollars_year", 2022)
        cost_escalator = self._kwargs.get("escalator", INFLATION_ESCALATOR)
        existing_install_cost = self._kwargs.get("existing_install_cost", 0)
        salvage_val = 0

        existing_adjusted_cost = existing_install_cost * (
            (1 - cost_escalator) ** (existing_cost_dollars_year - existing_install_year)
        )

        depreciation_rate = (existing_adjusted_cost - salvage_val) / lifetime

        existing_book_val = [
            max(existing_adjusted_cost - depreciation_rate * (i - existing_install_year), 0)
            for i in self._years_vec
        ]

        return existing_book_val
    
    def _get_replacement_vec(self) -> List[bool]:
        """
        The replacement vector is a vector of True when the index is the retrofit year, False o/w
        """
        replacement_year = self._kwargs.get("replacement_year", self._years_vec[-1])
        return [True if i==replacement_year else False for i in self._years_vec]

    def _get_existing_stranded_val(self) -> List[float]:
        stranded_val = np.multiply(self.existing_book_val, self._replacement_vec).tolist()
        return stranded_val
    
    def _get_replacement_cost(self) -> List[float]:
        replacement_cost = self._kwargs.get("replacement_cost", 0)
        replacement_year = self._kwargs.get("replacement_year", self._years_vec[-1])

        cost_escalator = self._kwargs.get("escalator", INFLATION_ESCALATOR)
        replacement_cost_dollars_year = self._kwargs.get("replacement_cost_dollars_year", 2022)

        replacement_cost = replacement_cost * (
            (1 + cost_escalator) ** (replacement_year - replacement_cost_dollars_year)
        )

        replacement_cost_vec = [
            replacement_cost if i==replacement_year else 0 for i in self._years_vec
        ]

        return replacement_cost_vec
    
    def _get_replacement_book_value(self) -> List[float]:
        replacement_cost = max(self.replacement_cost)
        replacement_year = self._kwargs.get("replacement_year", self._years_vec[-1])
        replacement_lifetime = self._kwargs.get(
            "replacement_lifetime",
            self._kwargs.get("lifetime", 10)
        )
        salvage_val = 0

        depreciation_rate = (replacement_cost - salvage_val) / replacement_lifetime

        replacement_book_val = [
            max(replacement_cost - depreciation_rate * (i - replacement_year), 0)
            if i >= replacement_year
            else 0
            for i in self._years_vec
        ]

        return replacement_book_val
    
    def _get_cost_table(self) -> pd.DataFrame:
        asset_type = self._kwargs.get("end_use", "hvac")

        values = {
            "{}_existing_book_value".format(asset_type): self.existing_book_val,
            "{}_replacement_vec".format(asset_type): np.array(self._replacement_vec, dtype=int),
            "{}_existing_stranded_value".format(asset_type): self.existing_stranded_val,
            "{}_replacement_cost".format(asset_type): self.replacement_cost,
            "{}_replacement_book_val".format(asset_type): self.replacement_book_val,
        }

        cost_table = pd.DataFrame(values, index=self._years_vec)

        return cost_table
