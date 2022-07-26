"""
NetworkEndUse parent class
"""
import numpy as np


class NetworkEndUse:
    """
    Defines the parent EndUse class for all end uses

    Args:
        install_year (int): The end use installation year
        end_use_cost (float): The end use cost, in $
        lifetime (int): The lifetime of the end use, in years
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
        depreciation_vector (list): List of depreciated value of end use at start of each year, in $
        stranded_value (list): Vector of the stranded value of the end use, in $

    Methods:
        initialize_end_use (None): Performs all calculations for the end use
        _get_install_cost (float): Returns the installation cost
    """
    def __init__(
        self,
        id, 
        parent_id,
        operation,
        install_year,
        install_cost,
        sim_start_year,
        sim_end_year,
        replacement_year
    ):
        #TODO: Need to decide what to do with install cost
        # If it is an existing end-use, then we should intake the install cost total and no calc needed
        # If new end-use, then we intake multiple cost factors (current sticker price, labor rate, escalator) and calc total cost
        self.install_year = install_year
        self.id = id
        self.parent_id = parent_id
        self.operation = operation
        self.install_cost = install_cost
        self.sim_start_year = sim_start_year
        self.sim_end_year = sim_end_year
        self.replacement_year = replacement_year

        self.install_cost: float = 0.
        self.operational_vector: list = []
        self.years_vector: list = []
        self.gas_leakage: list = []
        self.depreciation_vector: list = []
        self.stranded_value: list = []

    def initialize_end_use(self) -> None:
        self.install_cost = self.get_install_cost()
        self.operational_vector = self.get_operational_vector()
        self.years_vector = self.get_years_vector()
        self.gas_leakage = self.get_gas_leakage()
        self.depreciation_vector = self.get_depreciation()
        self.stranded_value = self.get_stranded_value()

    def get_install_cost(self) -> float:
        return 1.

    def get_operational_vector(self) -> list:
        """
        Operational vector of 1s and 0s. 1 means end use is in operation that year, 0 otherwise
        """
        sim_length = self.sim_end_year - self.sim_start_year
        sim_years = [self.sim_start_year + i for i in range(sim_length)]

        return [
            1 if self.install_year <= i and self.replacement_year > i
            else 0
            for i in sim_years
        ]

    def get_years_vector(self) -> list:
        return [
            self.sim_start_year + i
            for i in range(self.sim_end_year-self.sim_start_year)
        ]


    def get_gas_leakage(self) -> list:
        """
        Assume no gas leakage by default
        """
        return np.zeros(len(self.operational_vector)).tolist()

    def get_depreciation(self) -> list:
        """
        Assume depreciated value of 0 by default
        """
        return np.zeros(len(self.operational_vector)).tolist()

    def get_stranded_value(self) -> list:
        """
        Assume no stranded value by default
        """
        return np.zeros(len(self.operational_vector)).tolist()
