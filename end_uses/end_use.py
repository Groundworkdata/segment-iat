"""
EndUse parent class
"""
from dataclasses import replace
import numpy as np


class EndUse:
    """
    Defines the parent EndUse class for all end uses

    NOTE: sim_end_year is **exclusive**

    Methods:
        get_install_cost
        get_operational_vector
        get_elec_consump
        get_gas_consump
        get_depreciation
    """
    def __init__(
            self,
            install_year: int,
            install_cost: float,
            lifetime: int,
            elec_consump: float,
            gas_consump: float,
            sim_start_year: int,
            sim_end_year: int,
            replacement_year: int
    ):
        self.install_year = install_year
        self.install_cost: float = install_cost
        self.lifetime = lifetime
        self.elec_consump = elec_consump
        self.gas_consump = gas_consump
        self.sim_start_year = sim_start_year
        self.sim_end_year = sim_end_year
        self.replacement_year = replacement_year

        self.operational_vector: list = []
        self.years_vector: list = []
        self.total_elec_consump: list = []
        self.total_gas_consump: list = []

    def initialize_end_use(self) -> None:
        self.install_cost = self.get_install_cost()
        self.operational_vector = self.get_operational_vector()
        self.years_vector = self.get_years_vector()
        self.elec_consump_total = self.get_elec_consump()
        self.gas_consump_total = self.get_gas_consump()

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

    def get_depreciation(self) -> list:
        # TODO: Start with linear depreciation curve
        return (np.ones(len(self.operational_vector)) * np.array(self.operational_vector)).tolist()
