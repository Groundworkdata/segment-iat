"""
Defines distribution line parent class
"""
import pandas as pd
import numpy as np
from typing import List

from ttt.end_uses.utility_end_uses.utility_end_use import UtilityEndUse
from collections import Counter


class DistributionLine(UtilityEndUse):
    """
    Class definition for a distribution line

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
        connected_assets (list): List of associated downstream assets
        distribution_line_type (str): The type of distribution line

    Attributes:
        distribution_line_type (str): The type of distribution line
        loss_rate (int): Electric loss rate across the line
        connected_assets (list): List of associated downstream assets
        annual_total_energy_use (dict): Total annual energy use behind the meter, by sim year
        annual_peak_energy_use (dict): Total peak energy use at the meter, by sim year
        annual_energy_use_timeseries (dict): Hourly annual timeseries consumption at the meter, by sim year

    Methods:
        initialize_end_use (None): Executes all calculations for the meter
        get_elec_losses (list): List of elec losses over sim years
        get_annual_total_energy_use (dict): Gets the total energy use for the meter
        get_annual_peak_energy_use (dict): Gets the total energy demand for the meter
        get_annual_energy_use_timeseries (dict): Gets the energy use timeseries per year for the meter
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

        self.annual_total_energy_use: dict = {}
        self.annual_peak_energy_use: dict = {}
        self.annual_energy_use_timeseries: dict = {}

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

    def get_annual_energy_use_timeseries(self) -> dict:
        energy_timeseries = {i: pd.Series(0, index=self.year_timestamps) for i in self.years_vector}
        for i in self.years_vector:
            for meter in self.connected_assets:
                energy_timeseries[i] += meter.annual_energy_use_timeseries[i]

        return energy_timeseries
