"""
Parent _Asset class
"""
from typing import List

import numpy as np
import pandas as pd


class Asset:
    """
    Parent class for all assets

    Args:
        install_year (int): The install year of the asset
        asset_cost (float): The cost of the asset in present day dollars
            (or in $ from install year if installed prior to sim start)
        replacement_year (int): The replacement year of the asset
        lifetime (int): The asset lifetime in years
        sim_start_year (int): The simulation start year
        sim_end_year (int): The simulation end year (exclusive)

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

    Methods:
        initialize_end_use: Initializes the asset by calculating all derived variables
    """

    def __init__(
        self,
        inst_date: int,
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
        self.install_cost: List[float] = []
        self.depreciation: list = []
        self.stranded_value: list = []

    def initialize_end_use(self) -> None:
        self.years_vector = self.get_years_vector()
        self.year_timestamps = self.get_year_timestamps()
        self.operational_vector = self.get_operational_vector()
        self.retrofit_vector: list = [1 - i for i in self.operational_vector]
        # self.install_cost = self.get_install_cost()
        # self.depreciation = self.get_depreciation()
        # self.stranded_value = self.get_stranded_value()

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

        if operations_end > self.sim_end_year:
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
        replacement_ref = self.replacement_year - self.sim_start_year
        operational_lifetime = self.replacement_year - self.install_year

        stranded_val = np.zeros(len(self.operational_vector))

        # Handle when the replacement year is beyond the simulation end year
        if self.replacement_year > self.sim_end_year:
            return stranded_val.tolist()

        # Handle if replacement in final year and not fully depreciated
        elif (
            self.replacement_year == self.sim_end_year
            and operational_lifetime != self.lifetime
        ):
            replacement_ref = -1

        # Handle if replacement in final year and fully depreciated
        elif (
            self.replacement_year == self.sim_end_year
            and operational_lifetime == self.lifetime
        ):
            return stranded_val.tolist()

        stranded_val[replacement_ref] = self.depreciation[replacement_ref]
        return stranded_val.tolist()
