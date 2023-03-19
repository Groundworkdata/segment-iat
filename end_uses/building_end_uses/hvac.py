"""
Defines Stove end use
"""
from typing import Dict, List

import pandas as pd


ENERGY_KEYS = [
    "out.electricity.heating.energy_consumption",
    "out.electricity.cooling.energy_consumption",
    "out.natural_gas.heating.energy_consumption",
    "out.natural_gas.heating_hp_bkup.energy_consumption", # hybrid configuration
    "out.propane.heating.energy_consumption",
    "out.propane.heating_hp_bkup.energy_consumption", # hybrid configuration
    "out.fuel_oil.heating.energy_consumption",
    "out.fuel_oil.heating_hp_bkup.energy_consumption", #hybrid configuration
]

RESSTOCK_BASELINE_SCENARIO_ID = 0


class HVAC:
    """
    HVAC end use

    Args:
        resstock_metadata (dict): Need to include ResStock metadata of inputs so we can check if the
        retrofit water heater is gas and we need to convert to propane in the NPA scenario

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
            resstock_metadata: dict = None,
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

    #FIXME
    def get_install_cost(self):
        pass
