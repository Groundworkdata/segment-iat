"""
Defines meter parent class
"""
import numpy as np

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
            install_year: int,
            asset_cost: float,
            replacement_year: int,
            lifetime: int,
            sim_start_year: int,
            sim_end_year: int,
            asset_id: str,
            parent_id: str,
            building_id: str,
            building: Building,
            meter_type: str
    ):
        super().__init__(
            install_year,
            asset_cost,
            replacement_year,
            lifetime,
            sim_start_year,
            sim_end_year,
            asset_id,
            parent_id
        )

        self.building_id: list = building_id
        self.building: Building = building
        self.meter_type: str = meter_type

        self.total_annual_energy_use: list = []
        self.total_annual_peak_use: list = []

    def initialize_end_use(self) -> None:
        """
        Calculates aggregate consumption values behind the meter
        """
        super().initialize_end_use()
        if self.building:
            self.total_annual_energy_use = self.get_total_annual_energy_use()
            self.total_annual_peak_use = self.get_total_annual_peak_use()

    def get_total_annual_energy_use(self) -> list:
        """
        Get the total energy use behind the meter

        Returns:
            list: List of annual energy consumption
        """
        energy_attr = self.meter_type.lower() + "_consump_annual"
        end_uses = list(self.building.end_uses.get("stove").values())
        energy_consumps = [getattr(i, energy_attr) for i in end_uses]
        return np.array(energy_consumps).sum(axis=0).tolist()

    def get_total_annual_peak_use(self) -> list:
        energy_attr = self.meter_type.lower() + "_peak_annual"
        end_uses = list(self.building.end_uses.get("stove").values())
        energy_consumps = [getattr(i, energy_attr) for i in end_uses]
        return np.array(energy_consumps).sum(axis=0).tolist()
