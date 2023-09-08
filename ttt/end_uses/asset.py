"""
Parent Asset class
"""
from typing import List

import numpy as np
import pandas as pd


class Asset:
    """
    Parent class for all assets

    Args:
        inst_date (int): The install year of the asset
        inst_cost (float): The cost of the asset in present day dollars
            (or in $ from install year if installed prior to sim start)
        lifetime (int): Useful lifetime of the asset in years
        sim_start_year (int): The simulation start year
        sim_end_year (int): The simulation end year (exclusive)
        replacement_year (int): The replacement year of the asset

    Attributes:
        install_year (int): The install year of the asset
        asset_cost (float): The cost of the asset in present day dollars
            (or in $ from install year if installed prior to sim start)
        replacement_year (int): The replacement year of the asset
        lifetime (int): The asset lifetime in years
        sim_start_year (int): The simulation start year
        sim_end_year (int): The simulation end year (exclusive)
        years_vector (list): List of all years for the simulation
        year_timestamps (pd.DatetimeIndex): DatetimeIndex of hourly timestamps for a full year
        operational_vector (list): Boolean vals for years of the simulation when asset in operation
        retrofit_vector (list): Indicates that the asset has been retrofit; 1 for the retrofit year
            and all following years, 0 o/w
        replacement_vector (list): Indicates when the asset is retrofit; 1 in the retrofit year, 0 o/w
        install_cost (list): Install cost during the simulation years
        depreciation (list): Depreciated val during the simulation years
            (val is depreciated val at beginning of each year)
        stranded_value (list): Stranded asset val for early replacement during the simulation years
            (equal to the depreciated val at the replacement year)

    Methods:
        initialize_end_use (None): Initializes the asset by calculating all derived variables
        get_years_vector (list): Returns list of all simulation years
        get_year_timestamps (pd.DatetimeIndex): Returns hourly timestamps for a full year
        get_operational_vector (list): Returns list of 1 if asset in use that year, 0 o/w
        get_retrofit_vector (list): Return the asset retrofit_vector
        get_install_cost (list): Return list with annual install cost
        get_depreciation (list): Return list of annual depreciated value of the asset
        get_stranded_value (list): Return stranded value of asset after replacement
    """

    def __init__(
        self,
        inst_date: str,
        inst_cost: float,
        lifetime: int,
        sim_start_year: int,
        sim_end_year: int,
        replacement_year: int,
    ):
        self.install_year: int = int(inst_date.split("/")[2])
        self.asset_cost: float = inst_cost
        self.replacement_year: int = int(replacement_year)
        self.lifetime: int = lifetime
        self.sim_start_year: int = sim_start_year
        self.sim_end_year: int = sim_end_year

        self.years_vector: list = []
        self.year_timestamps: pd.DatetimeIndex = None
        self.operational_vector: list = []
        self.retrofit_vector: list = []
        self.replacement_vector: list = []
        self.install_cost: List[float] = []
        self.depreciation: list = []
        self.stranded_value: list = []

    def initialize_end_use(self) -> None:
        self.years_vector = self.get_years_vector()
        self.year_timestamps = self.get_year_timestamps()
        self.operational_vector = self.get_operational_vector()
        self.retrofit_vector = self.get_retrofit_vector()
        self.replacement_vector = self._get_replacement_vec()
        self.install_cost = self.get_install_cost()
        self.depreciation = self.get_depreciation()
        self.stranded_value = self.get_stranded_value()

    def get_years_vector(self) -> list:
        return [
            self.sim_start_year + i
            for i in range(self.sim_end_year - self.sim_start_year)
        ]

    def get_year_timestamps(self) -> pd.DatetimeIndex:
        return pd.date_range(
            start="2018-01-01", end="2019-01-01", freq="H", inclusive="left"
        )

    def get_operational_vector(self) -> list:
        """
        Operational vector of 1s and 0s. 1 means end use is in operation that year, 0 otherwise
        """
        sim_length = self.sim_end_year - self.sim_start_year
        sim_years = [self.sim_start_year + i for i in range(sim_length)]

        return [
            1 if self.install_year <= i and self.replacement_year > i else 0
            for i in sim_years
        ]
    
    def get_retrofit_vector(self) -> list:
        return [1 - i for i in self.operational_vector]
    
    def _get_replacement_vec(self) -> List[bool]:
        """
        The replacement vector is a vector of True when the index is the retrofit year, False o/w
        """
        return [True if i==self.replacement_year else False for i in self.years_vector]

    def get_install_cost(self) -> List[float]:
        """
        Assume install cost equal to the asset_cost input by default. Does not account for price
        escalation or inflation
        """
        install_cost = np.zeros(len(self.operational_vector)).tolist()

        if self.sim_start_year <= self.install_year <= self.sim_end_year:
            install_cost[self.install_year - self.sim_start_year] = self.asset_cost

        return install_cost

    def get_depreciation(self) -> List[float]:
        """
        Uses straight line depreciation and assumes no salvage value at end-of-life

        Vector represents depreciated end use value at year-beginning
        """
        depreciation_vec = np.zeros(len(self.operational_vector))
        salvage_value = 0
        depreciation_rate = (self.asset_cost - salvage_value) / self.lifetime

        operational_lifetime = min(
            self.replacement_year - self.install_year, self.lifetime
        )
        operations_end = self.install_year + operational_lifetime

        depreciated_value = np.array(
            [
                self.asset_cost - depreciation_rate * i
                for i in range(operational_lifetime + 1)
            ]
        )

        if operations_end >= self.sim_end_year:
            depreciated_value = depreciated_value[
                : self.sim_end_year - operations_end - 1
            ]

        depreciated_value = depreciated_value[
            max(0, self.sim_start_year - self.install_year) :
        ]

        depreciation_start_index = max(self.install_year - self.sim_start_year, 0)
        depreciation_end_index = min(
            max(self.install_year - self.sim_start_year, 0) + len(depreciated_value),
            len(depreciation_vec),
        )

        depreciation_vec[
            depreciation_start_index:depreciation_end_index
        ] = depreciated_value

        return depreciation_vec.tolist()

    def get_stranded_value(self) -> list:
        """
        Calculates the stranded value based on the depreciation vector

        Depreciation value and replacement is year-beginning, so references depreciated value at the
        replacement year

        Stranded value is 0 if the replacement year is outside of the sim timeframe
        """
        return (np.array(self.depreciation) * np.array(self.replacement_vector)).tolist()
