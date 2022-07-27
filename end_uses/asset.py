"""
Parent _Asset class
"""
import numpy as np


class Asset:
    """
    Parent class for all assets

    Args:
        install_year (int): The install year of the asset
        replacement_year (int): The replacement year of the asset
        sim_start_year (int): The simulation start year
        sim_end_year (int): The simulation end year (exclusive)

    Attributes:
        install_year (int): The install year of the asset
        replacement_year (int): The replacement year of the asset
        sim_start_year (int): The simulation start year
        sim_end_year (int): The simulation end year (exclusive)
        years_vector (list): List of all years for the simulation
        operational_vector (list): Boolean vals for years of the simulation when asset in operation
        install_cost (list): Install cost during the simulation years
        depreciation (list): Depreciated val at year start during the simulation years
        stranded_value (list): Stranded asset val for early replacement during the simulation years

    Methods:
        x
    """
    def __init__(
            self,
            install_year: int,
            replacement_year: int,
            sim_start_year: int,
            sim_end_year: int
    ):
        self.install_year: int = install_year
        self.replacement_year: int = replacement_year
        self.sim_start_year: int = sim_start_year
        self.sim_end_year: int = sim_end_year

        self.years_vector: list = []
        self.operational_vector: list = []
        self.install_cost: list = []
        self.depreciation: list = []
        self.stranded_value: list = []

    def initialize_end_use(self) -> None:
        self.years_vector = self.get_years_vector()
        self.operational_vector = self.get_operational_vector()
        self.install_cost = self.get_install_cost()
        self.depreciation = self.get_depreciation()
        self.stranded_value = self.get_stranded_value()

    def get_years_vector(self) -> list:
        return [
            self.sim_start_year + i
            for i in range(self.sim_end_year-self.sim_start_year)
        ]

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

    def get_install_cost(self) -> list:
        """
        Assume install cost of 0 by default
        """
        #TODO: Come up with generalized cost function for all assets (based on an input cost)
        return np.zeros(len(self.operational_vector)).tolist()

    def get_depreciation(self) -> list:
        """
        Assume depreciated value of 0 by default
        """
        #TODO: Update to a straight-line depreciation calculation (see Stove)
        return np.zeros(len(self.operational_vector)).tolist()

    def get_stranded_value(self) -> list:
        """
        Assume no stranded value by default
        """
        #TODO: Update to the stranded value calculation seen in Stove
        return np.zeros(len(self.operational_vector)).tolist()
