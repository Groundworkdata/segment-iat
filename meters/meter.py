"""
Defines meter parent class
"""
import numpy as np


class Meter:
    """
    Defines a meter parent class. A Meter sums energy consumptions of all end uses

    Args:
        end_uses (list): List of end use instances (Stove, etc)
        meter_type (str): The type of meter (ELEC, GAS)

    Attributes:
        end_uses (list): List of end use instances (Stove, etc)
        meter_type (str): The type of meter (ELEC, GAS)

    Methods:
        get_total_energy_use (np.array): Gets the total energy use for the meter
        get_total_energy_demand (None): Gets the total energy demand for the meter
    """
    def __init__(self, end_uses: list, meter_type: str):
        self.end_uses: list = end_uses
        self.meter_type: str = meter_type

        self.total_energy_use: list = []

    def initialize_meter(self) -> None:
        self.total_energy_use = self.get_total_energy_use()

    def get_total_energy_use(self) -> np.array:
        energy_attr = self.meter_type.lower() + "_consump_total"
        energy_consumps = [getattr(i, energy_attr) for i in self.end_uses]
        return np.array(energy_consumps).sum(axis=0).tolist()

    #TODO: Implement after getting example timeseries data
    def get_total_energy_demand(self) -> None:
        """
        Need to also calculate the total demand (power) of all end uses
        """
        raise NotImplementedError
