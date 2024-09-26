"""
Defines a clothes dryer asset
"""
from typing import List

import numpy as np
import pandas as pd

from segment_iat.end_uses.building_end_uses.building_measure import BuildingMeasure


ENERGY_KEYS = [
    "out.electricity.clothes_dryer.energy_consumption",
    "out.natural_gas.clothes_dryer.energy_consumption",
    "out.propane.clothes_dryer.energy_consumption",
]

DEFAULT_ASSET_LIFETIME = 30


class ClothesDryer(BuildingMeasure):
    """
    Clothes dryer building measure. Inherits from BuildingMeasures

    Args:
        years_vec (List[int]): List of simulation years
        incentive_data (List[dict]): Applicable incentives for the measure
        custom_baseline_energy (pd.DataFrame): Custom input timeseries of baseline energy consump
        custom_retrofit_energy (pd.DataFrame): Custom input timeseries of retrofit energy consump

    Keyword Args:
        existing_install_year (int): Install year of the baseline asset
        lifetime (int): Useful lifetime of the asset in years
        replacement_cost_dollars_year (int): Reference year for the input costs
        escalator (float): Inflation escalator for cost calculations
        existing_install_cost (float): Installation cost of the baseline asset
        replacement_year (int): Year of retrofit
        replacement_cost (float): Cost of replacing asset
        replacement_lifetime (int): Useful lifetime of the replacement asset in years
        end_use (str): The asset type
    """
    def __init__(
            self,
            years_vec: List[int],
            incentive_data,
            custom_baseline_energy: pd.DataFrame = pd.DataFrame(),
            custom_retrofit_energy: pd.DataFrame = pd.DataFrame(),
            **kwargs
    ):
        
        super().__init__(
            years_vec,
            incentive_data,
            ENERGY_KEYS,
            DEFAULT_ASSET_LIFETIME,
            custom_baseline_energy,
            custom_retrofit_energy,
            **kwargs
        )
