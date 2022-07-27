"""
EndUse parent class
"""
import numpy as np

from end_uses.asset import Asset


class BuildingEndUse(Asset):
    """
    Defines the parent BuildingEndUse class for all building-level end uses. Inherits from Asset

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
        end_use_cost (float): The end use cost, in $
        lifetime (int): The lifetime of the end use, in years
        elec_consump (float): The total annual elec consump, in kWh
        gas_consump (float): The total annual gas consump, in kWh
        total_elec_consump (list): The total annual elec consump of the end use, in kWh
        total_gas_consump (list): The total annual gas consump of the end use, in kWh
        gas_leakage (list): List of annual gas leakage from end use, in kWh

    Methods:
        initialize_end_use (None): Performs all calculations for the end use
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
        super().__init__(
            install_year,
            replacement_year,
            sim_start_year,
            sim_end_year
        )

        #TODO: Need to decide what to do with install cost
        # If it is an existing end-use, then we should intake the install cost total and no calc needed
        # If new end-use, then we intake multiple cost factors (current sticker price, labor rate, escalator) and calc total cost
        self.end_use_cost: float = end_use_cost
        self.lifetime = lifetime
        self.elec_consump = elec_consump
        self.gas_consump = gas_consump

        self.total_elec_consump: list = []
        self.total_gas_consump: list = []
        self.gas_leakage: list = []

    def initialize_end_use(self) -> None:
        super().initialize_end_use()
        self.elec_consump_total = self.get_elec_consump()
        self.gas_consump_total = self.get_gas_consump()
        self.gas_leakage = self.get_gas_leakage()

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
