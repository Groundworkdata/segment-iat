"""
Defines meter parent class
"""
import numpy as np
from typing import List

from buildings.building import Building
from end_uses.utility_end_uses.utility_end_use import UtilityEndUse


class Meter(UtilityEndUse):
    """
    Defines a meter parent class. A Meter sums energy consumptions of all end uses

    Args:
        install_year (int): The install year of the asset
        asset_cost (float): The cost of the asset in present day dollars
            (or in $ from install year if installed prior to sim start)
        replacement_year (int): The replacement year of the asset
        lifetime (int): The asset lifetime in years
        sim_start_year (int): The simulation start year
        sim_end_year (int): The simulation end year (exclusive)
        asset_id (str): The ID for the given asset
        parent_id (str): The ID for the parent of the asset (if applicable, otherwise empty)
        building_id (str): The ID of the associated building for the meter
        building (Building): Instance of the associated Building object
        meter_type (str): The type of meter (ELEC, GAS)

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
        asset_id (str): The ID for the given asset
        parent_id (str): The ID for the parent of the asset (if applicable, otherwise empty)
        building_id (str): The ID of the associated building for the meter
        building (Building): Instance of the associated Building object
        meter_type (str): The type of meter (ELEC, GAS)
        total_annual_energy_use (list): Total annual energy use behind the meter

    Methods:
        get_total_annual_energy_use (list): Gets the total energy use for the meter
        get_total_annual_peak_use (list): Gets the total energy demand for the meter
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
        building: Building,
        meter_type: str,
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

        self.building: Building = building
        self.meter_type: str = meter_type

        self.annual_total_energy_use: dict = []
        self.annual_peak_energy_use: dict = []
        self.annual_energy_use_timeseries: dict = []

    def initialize_end_use(self) -> None:
        """
        Calculates aggregate consumption values behind the meter
        """
        super().initialize_end_use()
        if self.building:
            self.annual_total_energy_use = self.get_annual_total_energy_use()
            self.annual_peak_energy_use = self.get_annual_peak_energy_use()
            self.annual_energy_use_timeseries = self.get_annual_energy_use_timeseries()

    def get_annual_total_energy_use(self) -> dict:
        """
        Get the total energy use behind the meter

        Returns:
            list: List of annual energy consumption
        """
        energy_attr = "out." + self.meter_type.lower() + ".total.energy_consumption"
        annual_total_energy_baseline = np.sum(
            self.building.baseline_consumption[[energy_attr]]
        ).values[0]
        annual_total_energy_retrofit = np.sum(
            self.building.retrofit_consumption[[energy_attr]]
        ).values[0]

        annual_total_energy = [
            annual_total_energy_baseline * operation
            + annual_total_energy_retrofit * retrofit
            for operation, retrofit in zip(
                self.operational_vector, self.retrofit_vector
            )
        ]

        return dict(zip(self.years_vector, annual_total_energy))

    def get_annual_peak_energy_use(self) -> dict:
        energy_attr = "out." + self.meter_type.lower() + ".total.energy_consumption"

        annual_peak_energy_baseline = (
            self.building.baseline_consumption[[energy_attr]].max().values[0]
        )
        annual_peak_energy_retrofit = (
            self.building.retrofit_consumption[[energy_attr]].max().values[0]
        )

        annual_peak_energy = [
            annual_peak_energy_baseline * operation
            + annual_peak_energy_retrofit * retrofit
            for operation, retrofit in zip(
                self.operational_vector, self.retrofit_vector
            )
        ]

        return dict(zip(self.years_vector, annual_peak_energy))

    def get_annual_energy_use_timeseries(self) -> list:
        energy_attr = "out." + self.meter_type.lower() + ".total.energy_consumption"

        annual_energy_use_baseline = self.building.baseline_consumption[[energy_attr]]
        annual_energy_use_retrofit = self.building.retrofit_consumption[[energy_attr]]

        annual_energy_use_timeseries = [
            annual_energy_use_baseline if i == 1 else annual_energy_use_retrofit
            for i in self.operational_vector
        ]

        return dict(zip(self.years_vector, annual_energy_use_timeseries))

    # TODO: Add aggregation of timeseries consumption
