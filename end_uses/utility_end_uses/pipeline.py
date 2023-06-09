"""
Defines meter parent class
"""
import numpy as np
import pandas as pd
from typing import List

from end_uses.utility_end_uses.utility_end_use import UtilityEndUse
from collections import Counter


class Pipeline(UtilityEndUse):
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

        self.pipeline_type: str = pipeline_type
        self.length: int = length_ft
        #TODO: What to do when length is None
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
        leakage_factor_file = "./config_files/leakage_data/leakage_factors.csv"
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
        tmp_counter = Counter()
        # for meter in self.connected_assets:
        #     print(meter.annual_energy_use_timeseries)
        # TODO: Add aggregation of timeseries consumption
        # tmp_counter.update(meter.annual_total_energy_use)

        return dict(tmp_counter)

    def get_annual_total_leakage(self) -> list:
        leakage_factor = float(self.leakage_factors[
            (self.leakage_factors["asset"] == self.pipeline_type)
            & (self.leakage_factors["code"] == self.material)
        ].value * self.length)

        # TODO: check if the units of length and leakage factor match

        annual_leakage = [i*leakage_factor for i in self.operational_vector]

        for idx, retrofit in enumerate(self.retrofit_vector):
            if retrofit:
                leakage_factor = float(
                    self.leakage_factors[
                        (self.leakage_factors["asset"] == self.pipeline_type)
                        & (self.leakage_factors["code"] == "PL")
                    ].value
                )

                annual_leakage[idx] = leakage_factor * self.length

        return (np.array(annual_leakage) * np.array(self.operational_vector)).tolist()
