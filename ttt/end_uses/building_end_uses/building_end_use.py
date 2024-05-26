"""
EndUse parent class
"""
#TODO: Remove or update and integrate with discrete end uses -- class currently not in use
import json
from typing import Dict

import numpy as np
import pandas as pd

from ttt.end_uses.asset import Asset


class BuildingEndUse(Asset):
    """
    Defines the parent BuildingEndUse class for all building-level end uses. Inherits from Asset

    Args:
        None

    Keyword Args:
        install_year (int): The install year of the asset
        asset_cost (float): The cost of the asset in present day dollars
            (or in $ from install year if installed prior to sim start)
        replacement_year (int): The replacement year of the asset
        lifetime (int): The asset lifetime in years
        sim_start_year (int): The simulation start year
        sim_end_year (int): The simulation end year (exclusive)
        elec_consump (float): The total annual elec consump, in kWh
        gas_consump (float): The total annual gas consump, in kWh
        building_id (str): Identifies the building where the end use is located

    Attributes:
        install_year (int): The install year of the asset
        asset_cost (float): The cost of the asset in present day dollars
            (or in $ from install year if installed prior to sim start)
        replacement_year (int): The replacement year of the asset
        lifetime (int): The asset lifetime in years
        sim_start_year (int): The simulation start year
        sim_end_year (int): The simulation end year (exclusive)
        years_vector (list): List of all years for the simulation
        operational_vector (list): Boolean vals for years of the simulation when asset in operation
        install_cost (list): Install cost during the simulation years
        depreciation (list): Depreciated val during the simulation years
            (val is depreciated val at beginning of each year)
        stranded_value (list): Stranded asset val for early replacement during the simulation years
            (equal to the depreciated val at the replacement year)
        elec_consump (Dict[str, float]): Timeseries elec consump of the end use for one year, in kWh
        gas_consump (Dict[str, float]): Timeseries gas consump of the end use for one year, in kWh
        elec_consump_annual (list): The total annual elec consump of the end use, in kWh
        gas_consump_annual (list): The total annual gas consump of the end use, in kWh
        elec_peak_annual (list): Annual peak elec consump, in kW
        gas_peak_annual (list): Annual peak gas consump, in kW
        gas_leakage (list): List of annual gas leakage from end use, in kWh
        building_id (str): Identifies the building where the end use is located

    Methods:
        initialize_end_use (None): Performs all calculations for the end use
    """
    def __init__(self, **kwargs):
        super().__init__(
            kwargs.get("install_year"),
            kwargs.get("asset_cost"),
            kwargs.get("replacement_year"),
            kwargs.get("lifetime"),
            kwargs.get("sim_start_year"),
            kwargs.get("sim_end_year")
        )

        self._elec_consump_filepath = kwargs.get("elec_consump")
        self._gas_consump_filepath = kwargs.get("gas_consump")

        self.building_id: str = kwargs.get("building_id")

        self.elec_consump: dict = {}
        self.gas_consump: dict = {}
        self.elec_consump_annual: list = []
        self.gas_consump_annual: list = []
        self.elec_peak_annual: list = []
        self.gas_peak_annual: list = []

        self.gas_leakage: list = []

    def initialize_end_use(self) -> None:
        """
        Expands on parent initialize_end_use method to calculate additional values
        """
        super().initialize_end_use()
        self.elec_consump = self.read_elec_consump()
        self.gas_consump = self.read_gas_consump()
        self.elec_consump_annual = self.get_elec_consump()
        self.gas_consump_annual = self.get_gas_consump()
        self.elec_peak_annual = self.get_elec_peak_annual()
        self.gas_peak_annual = self.get_gas_peak_annual()
        self.gas_leakage = self.get_gas_leakage()

    def read_elec_consump(self) -> Dict[str, float]:
        """
        Read the electric consumption data file

        Returns:
            Dict[str, float]: Dict of timeseries data indexed by ISO-formatted datetime strings
        """
        with open(self._elec_consump_filepath) as f:
            data = json.load(f)

        return data

    def read_gas_consump(self) -> Dict[str, float]:
        with open(self._gas_consump_filepath) as f:
            data = json.load(f)

        return data

    def get_elec_consump(self) -> list[float]:
        elec_consump = pd.Series(self.elec_consump)
        elec_consump.index = pd.DatetimeIndex(elec_consump.index)
        elec_consump_annual = elec_consump.sum(axis=0)
        elec_consump_annual = (elec_consump_annual * np.array(self.operational_vector)).tolist()

        return elec_consump_annual

    def get_gas_consump(self) -> list[float]:
        gas_consump = pd.Series(self.gas_consump)
        gas_consump.index = pd.DatetimeIndex(gas_consump.index)
        gas_consump_annual = gas_consump.sum(axis=0)
        gas_consump_annual = (gas_consump_annual * np.array(self.operational_vector)).tolist()

        return gas_consump_annual

    def get_elec_peak_annual(self) -> list:
        elec_consump = pd.Series(self.elec_consump)
        elec_consump.index = pd.DatetimeIndex(elec_consump.index)
        elec_peak_annual = elec_consump.max()
        elec_peak_annual = (elec_peak_annual * np.array(self.operational_vector)).tolist()

        return elec_peak_annual

    def get_gas_peak_annual(self) -> list:
        gas_consump = pd.Series(self.gas_consump)
        gas_consump.index = pd.DatetimeIndex(gas_consump.index)
        gas_peak_annual = gas_consump.max()
        gas_peak_annual = (gas_peak_annual * np.array(self.operational_vector)).tolist()

        return gas_peak_annual

    def get_gas_leakage(self) -> list:
        """
        Assume no gas leakage by default
        """
        return np.zeros(len(self.operational_vector)).tolist()
