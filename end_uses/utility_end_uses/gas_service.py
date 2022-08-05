"""
Defines Gas Service end use
"""
import numpy as np
from typing import List

from end_uses.utility_end_uses.utility_end_use import UtilityEndUse


class GasService(UtilityEndUse):
    """
    Gas service end use. Inherits parent UtilityEndUse class

    Args:
        None

    Keyword Args:
        install_year (int): The install year of the asset
        asset_cost (float): The cost of the asset in present day dollars
            (or in $ from install year if installed prior to sim start)
        replacement_year (int): The replacement year of the asset
        lifetime (int): The asset lifetime in years
        sim_start_year (int): The simulation start year
        sim_end_year (int): The simulation end year (exclusive)
        asset_id (str): The ID for the given asset
        parent_id (str): The ID for the parent of the asset (if applicable, otherwise empty)
        length (int): Length of the gas main in **UNITS**
        diameter (int): Diameter of the gas main in **UNITS**
        material (str): The material type of the gas main. **Options: []**
        safety_ratings (?): ?
        leak_rate (float): The leak rate of the main in **UNITS**
        end_of_life (?): ?

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
        length (int): Length of the gas main in **UNITS**
        diameter (int): Diameter of the gas main in **UNITS**
        material (str): The material type of the gas main. **Options: []**
        safety_ratings (?): ?
        leak_rate (float): The leak rate of the main in **UNITS**
        end_of_life (?): ?

    Methods:
        get_gas_leakage (list): Gets annual gas leakage for the main
    """
    def __init__(self, **kwargs):
        super().__init__(
            kwargs.get("install_year"),
            kwargs.get("asset_cost"),
            kwargs.get("replacement_year"),
            kwargs.get("lifetime"),
            kwargs.get("sim_start_year"),
            kwargs.get("sim_end_year"),
            kwargs.get("asset_id"),
            kwargs.get("parent_id")
        )

        self.length: int = kwargs.get("length")
        self.diameter: int = kwargs.get("diameter")
        self.material: str = kwargs.get("material")
        self.safety_ratings: float = kwargs.get("safety_ratings")
        self.leak_rate: float = kwargs.get("leak_rate")
        self.end_of_life: float = kwargs.get("end_of_life")

    def get_gas_leakage(self) -> list:
        """
        Gets annual gas leakage for the main
        """
        return np.repeat(self.leak_rate, len(self.operational_vector))
