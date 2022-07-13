"""
EndUse parent class
"""
from dataclasses import replace
import numpy as np


class EndUse:
    """
    Defines the parent EndUse class for all end uses

    Args:
        install_year (int): The end use installation year
        end_use_cost (float): The end use cost, in $
        lifetime (int): The lifetime of the end use, in years
        elec_consump (float): The total annual elec consump, in kWh
        gas_consump (float): The total annual gas consump, in kWh
        sim_start_year (int): The starting year of the simulation
        sim_end_year (int): The end year of the simulation, exclusive
        replacement_year (int): The year of end use replacement

    Attributes:
        install_year (int): The end use installation year
        end_use_cost (float): The end use cost, in $
        lifetime (int): The lifetime of the end use, in years
        elec_consump (float): The total annual elec consump, in kWh
        gas_consump (float): The total annual gas consump, in kWh
        sim_start_year (int): The starting year of the simulation
        sim_end_year (int): The end year of the simulation, exclusive
        replacement_year (int): The year of end use replacement
        operational_vector (list): Defines years of operation.
            1 indicates asset in operation that year, else 0
        years_vector (list): List of all years in the simulation
        total_elec_consump (list): The total annual elec consump of the end use, in kWh
        total_gas_consump (list): The total annual gas consump of the end use, in kWh
        gas_leakage (list): List of annual gas leakage from end use, in kWh
        depreciation_vector (list): List of depreciated value of end use each year, in $

    Methods:
        initialize_end_use (None): Performs all calculations for the end use
        _get_install_cost (float): Returns the installation cost
    """
    def __init__(
            self,
            install_year: int,
            end_use_cost: float,
            lifetime: int,
            elec_consump: float,
            gas_consump: float,
            sim_start_year: int,
            sim_end_year: int,
            replacement_year: int
    ):
        #TODO: Need to decide what to do with install cost
        # If it is an existing end-use, then we should intake the install cost total and no calc needed
        # If new end-use, then we intake multiple cost factors (current sticker price, labor rate, escalator) and calc total cost
        self.install_year = install_year
        self.end_use_cost: float = end_use_cost
        self.lifetime = lifetime
        self.elec_consump = elec_consump
        self.gas_consump = gas_consump
        self.sim_start_year = sim_start_year
        self.sim_end_year = sim_end_year
        self.replacement_year = replacement_year

        self.install_cost: float = 0.
        self.operational_vector: list = []
        self.years_vector: list = []
        self.total_elec_consump: list = []
        self.total_gas_consump: list = []
        self.gas_leakage: list = []
        self.depreciation_vector: list = []

    def initialize_end_use(self) -> None:
        self.install_cost = self.get_install_cost()
        self.operational_vector = self.get_operational_vector()
        self.years_vector = self.get_years_vector()
        self.elec_consump_total = self.get_elec_consump()
        self.gas_consump_total = self.get_gas_consump()
        self.gas_leakage = self.get_gas_leakage()
        self.depreciation_vector = self.get_depreciation()

    def get_install_cost(self) -> float:
        return 1.

    def get_operational_vector(self) -> list:
        """
        Operational vector of 1s and 0s
        """
        # TODO: Need to include the retrofit year in this calc
        return np.concatenate([
            np.ones(self.replacement_year-self.sim_start_year, dtype=int),
            np.zeros(self.sim_end_year-self.replacement_year, dtype=int)
        ]).tolist()

    def get_years_vector(self) -> list:
        return [
            self.sim_start_year + i
            for i in range(self.sim_end_year-self.sim_start_year)
        ]

    def get_elec_consump(self) -> list:
        # TODO: Decide on format and populate with dummy data
        return (np.ones(len(self.operational_vector)) * np.array(self.operational_vector)).tolist()

    def get_gas_consump(self) -> list:
        # TODO: Decide on format and populate with dummy data
        return (np.ones(len(self.operational_vector)) * np.array(self.operational_vector)).tolist()

    def get_gas_leakage(self) -> list:
        """
        Assume no gas leakage by default
        """
        return np.zeros(len(self.operational_vector)).tolist()

    def get_depreciation(self) -> list:
        # TODO: Start with linear depreciation curve
        return (np.ones(len(self.operational_vector)) * np.array(self.operational_vector)).tolist()
