"""
Defines meter parent class
"""
import pandas as pd
import numpy as np
from typing import List

from end_uses.utility_end_uses.utility_end_use import UtilityEndUse
from collections import Counter


class DistributionLine(UtilityEndUse):
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
        decarb_scenario: int,
        connected_assets: list,
        distribution_line_type: str,
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

        self.distribution_line_type: str = distribution_line_type

        self.loss_rate: int = 2
        # TODO: update based on the sec_wtype etc.
        self.connected_assets: list = connected_assets

        self.annual_total_energy_use: dict = []
        self.annual_peak_energy_use: dict = []
        self.annual_energy_use_timeseries: dict = []

    def initialize_end_use(self) -> None:
        """
        Calculates aggregate consumption values behind the meter
        """
        super().initialize_end_use()
        if self.connected_assets:
            self.annual_total_energy_use = self.get_annual_total_energy_use()
            self.annual_energy_use_timeseries = self.get_annual_energy_use_timeseries()
            self.annual_peak_energy_use = self.get_annual_peak_energy_use()
            self.get_elec_losses()

    def get_elec_losses(self) -> list:
        """
        Gets annual loss rate for the main
        """
        # TODO: update it to dictionary
        return np.repeat(self.loss_rate, len(self.operational_vector))

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
        annual_peak = []

        for i in self.years_vector:
            annual_peak.append(self.annual_energy_use_timeseries[i].max())

        return annual_peak

    def get_annual_energy_use_timeseries(self) -> list:
        energy_timeseries = {i: pd.Series(0, index=self.year_timestamps) for i in self.years_vector}
        for i in self.years_vector:
            for meter in self.connected_assets:
                energy_timeseries[i] += meter.annual_energy_use_timeseries[i]

        return energy_timeseries
