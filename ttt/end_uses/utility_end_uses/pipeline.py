"""
Defines pipeline parent class
"""
import numpy as np
import pandas as pd
from typing import List

from ttt.end_uses.utility_end_uses.utility_end_use import UtilityEndUse
from collections import Counter


class Pipeline(UtilityEndUse):
    """
    Defines a gas main pipeline, which inherits Pipeline class

    Args:
        gisid (str): The ID for the given asset
        parentid (str): The ID for the parent of the asset (if applicable, otherwise empty)
        inst_date (int): The install year of the asset
        inst_cost (float): The cost of the asset in present day dollars
            (or in $ from install year if installed prior to sim start)
        lifetime (int): Useful lifetime of the asset in years
        sim_start_year (int): The simulation start year
        sim_end_year (int): The simulation end year (exclusive)
        replacement_year (int): The replacement year of the asset
        decarb_scenario (str): The energy retrofit intervention scenario
        length_ft (int): Pipeline length in feet
        pressure (str): Rated pressure of the pipe
        diameter (str): Diameter of the pipe
        material (str): The pipe material
        connected_assets (list): List of associated downstream assets
        pipeline_type (str): The type of pipeline (gas_service, gas_main)

    Attributes:
        pipeline_type (str): The type of pipeline (gas_service, gas_main)
        length (int): Pipeline length in feet
        pressure (str): Rated pressure of the pipe
        diameter (str): Diameter of the pipe
        material (str): The pipe material
        leak_rate (int): The pipe's methane leak rate
        connected_assets (list): List of associated downstream assets
        decarb_scenario (str): The energy retrofit intervention scenario
        leakage_factors (pd.DataFrame): Table of methane leak factors by pipe material
        annual_total_leakage (list): List of total methane leaks by year
        annual_total_energy_use (dict): Total annual energy use behind the pipe, by sim year
        annual_peak_energy_use (dict): Total peak energy use at the pipe, by sim year
        annual_energy_use_timeseries (dict): Hourly annual timeseries consumption at the pipe, by sim year

    Methods:
        initialize_end_use (None): Executes all calculations for the pipe
        get_annual_total_energy_use (dict): Gets the total energy use for the pipe
        get_annual_peak_energy_use (dict): Gets the total energy demand for the pipe
        get_annual_energy_use_timeseries (dict): Gets the energy use timeseries per year for the pipe
        get_annual_total_leakage (list): Calculates the annual methane leaks from the pipe
    """
    def __init__(
        self,
        gisid: str,
        parentid: str,
        inst_date: int,
        inst_cost: float,
        lifetime: int,
        sim_start_year: int,
        sim_end_year: int,
        replacement_year: int,
        decarb_scenario: str,
        length_ft: int,
        pressure: str,
        diameter: str,
        material: str,
        connected_assets: list,
        segment_id: str,
        pipeline_type: str,
    ):
        super().__init__(
            gisid,
            parentid,
            inst_date,
            inst_cost,
            lifetime,
            sim_start_year,
            sim_end_year,
            replacement_year,
        )

        self._segment_id: str = segment_id

        self.pipeline_type: str = pipeline_type
        self.length: int = length_ft

        if not self.length:
            self.length = 1

        self.pressure: str = pressure
        self.diameter: str = diameter
        self.material: str = material

        self.leak_rate: int = 2
        # TODO: update based on the material etc.
        self.connected_assets: list = connected_assets

        self.decarb_scenario: str = decarb_scenario

        self.leakage_factors: pd.DataFrame = None

        self.annual_total_leakage: list = []
        self.annual_total_energy_use: dict = {}
        self.annual_peak_energy_use: dict = {}
        self.annual_energy_use_timeseries: dict = {}

    def _read_csv_config(self, config_file_path=None) -> None:
        """
        Read in the utilty network config file and save to network_config attr
        """
        data = pd.read_csv(config_file_path)
        return data

    def initialize_end_use(self) -> None:
        """
        Calculates aggregate consumption values behind the meter
        """
        super().initialize_end_use()
        if self.connected_assets:
            self.leakage_factors = self._load_leakage_factors()
            self.annual_total_energy_use = self.get_annual_total_energy_use()
            self.annual_peak_energy_use = self.get_annual_peak_energy_use()
            self.annual_energy_use_timeseries = self.get_annual_energy_use_timeseries()
            self.annual_total_leakage = self.get_annual_total_leakage()

    def _load_leakage_factors(self) -> int:
        leakage_factor_file = f"./config_files/{self._segment_id}/utility_network/{self._segment_id}_leakage_factors.csv"
        return self._read_csv_config(config_file_path=leakage_factor_file)

    def get_annual_total_energy_use(self) -> dict:
        """
        Get the total energy use on a gas service lines

        Returns:
            list: List of annual energy consumption
        """
        tmp_counter = Counter()
        for meter in self.connected_assets:
            tmp_counter.update(meter.annual_total_energy_use)

        return dict(tmp_counter)

    def get_annual_peak_energy_use(self) -> dict:
        tmp_counter = Counter()
        for meter in self.connected_assets:
            tmp_counter.update(meter.annual_peak_energy_use)

        return dict(tmp_counter)

    def get_annual_energy_use_timeseries(self) -> list:
        #TODO
        tmp_counter = Counter()

        return dict(tmp_counter)

    def get_annual_total_leakage(self) -> list:
        leakage_factor = self.leakage_factors[
            (self.leakage_factors["asset"] == self.pipeline_type)
            & (self.leakage_factors["code"] == self.material)
        ].loc[:, "value"].iloc[0] * self.length

        # TODO: check if the units of length and leakage factor match

        annual_leakage = [i*leakage_factor for i in self.operational_vector]

        for idx, retrofit in enumerate(self.retrofit_vector):
            if retrofit:
                leakage_factor = self.leakage_factors[
                    (self.leakage_factors["asset"] == self.pipeline_type)
                    & (self.leakage_factors["code"] == "PL")
                ].loc[:, "value"].iloc[0]

                annual_leakage[idx] = leakage_factor * self.length

        return (np.array(annual_leakage) * np.array(self.operational_vector)).tolist()
