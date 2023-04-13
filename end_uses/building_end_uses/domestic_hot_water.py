"""
Defines Stove end use
"""
from typing import Dict, List

import numpy as np
import pandas as pd


ENERGY_KEYS = [
    "out.electricity.hot_water.energy_consumption",
    "out.natural_gas.hot_water.energy_consumption",
    "out.propane.hot_water.energy_consumption",
    "out.fuel_oil.hot_water.energy_consumption",
]

RESSTOCK_BASELINE_SCENARIO_ID = 0


class DHW:
    """
    Domestic Hot Water end use

    Args:
        resstock_metadata (dict): Need to include ResStock metadata of inputs so we can check if the
        retrofit water heater is gas and we need to convert to propane in the NPA scenario

    Keyword Args:
        existing_install_year
        lifetime
        existing_install_cost
        replacement_cost
        replacement_year
        replacement_cost_dollars_year
        replacement_lifetime

    Attributes:
        ?

    Methods:
        ?
    """
    def __init__(
            self,
            energy_source: str,
            resstock_consumptions: Dict[int, pd.DataFrame],
            scenario_mapping: List[Dict],
            scenario: int,
            resstock_metadata: dict,
            years_vec: List[int],
            **kwargs
    ):
        self._kwargs = kwargs

        self.energy_source: str = energy_source
        self._resstock_consumps: Dict[int, pd.DataFrame] = resstock_consumptions
        self._scenario_mapping: List[Dict] = scenario_mapping
        self._scenario: int = scenario
        self._resstock_metadata = resstock_metadata
        self._years_vec: List[int] = years_vec

        self.existing_book_val: List[float] = []
        self.replacement_vec: List[bool] = []
        self.replacement_cost: List[float] = []
        self.replacement_book_val: List[float] = []
        self.cost_table: pd.DataFrame = None

        self.baseline_energy_use = None
        self._resstock_retrofit_scenario_id: int = None
        self.retrofit_energy_use = None

    def initialize_end_use(self) -> None:
        """
        Initialize the end use and calculate values
        """
        self.existing_book_val = self._get_existing_book_val()
        self.replacement_vec = self._get_replacement_vec()
        self.existing_stranded_val = self._get_existing_stranded_val()
        self.replacement_cost = self._get_replacement_cost()
        self.replacement_book_val = self._get_replacement_book_value()
        self.cost_table = self._get_cost_table()

        self.baseline_energy_use = self._get_energy_consump_baseline()
        self._resstock_retrofit_scenario_id = self._get_retrofit_scenario()
        self.retrofit_energy_use = self._get_energy_consump_retrofit()

    def _get_energy_consump_baseline(self) -> pd.DataFrame:
        return self._resstock_consumps[RESSTOCK_BASELINE_SCENARIO_ID][ENERGY_KEYS]

    def _get_retrofit_scenario(self) -> int:
        retrofits = self._scenario_mapping[self._scenario]
        return retrofits.get("dhw_resstock_scenario")

    def _get_energy_consump_retrofit(self) -> pd.DataFrame:
        return self._resstock_consumps[self._resstock_retrofit_scenario_id][ENERGY_KEYS]

    def _get_existing_book_val(self) -> List[float]:
        existing_install_year = self._kwargs.get("existing_install_year", self._years_vec[0])
        lifetime = self._kwargs.get("lifetime", 10)
        existing_install_cost = self._kwargs.get("existing_install_cost", 0)
        salvage_val = 0

        depreciation_rate = (existing_install_cost - salvage_val) / lifetime

        existing_book_val = [
            max(existing_install_cost - depreciation_rate * (i - existing_install_year), 0)
            for i in self._years_vec
        ]

        return existing_book_val
    
    def _get_replacement_vec(self) -> List[bool]:
        """
        The replacement vector is a vector of True when the index is the retrofit year, False o/w
        """
        replacement_year = self._kwargs.get("replacement_year", self._years_vec[-1])
        return [True if i==replacement_year else False for i in self._years_vec]

    def _get_existing_stranded_val(self) -> List[float]:
        stranded_val = np.multiply(self.existing_book_val, self.replacement_vec).tolist()
        return stranded_val
    
    def _get_replacement_cost(self) -> List[float]:
        replacement_cost = self._kwargs.get("replacement_cost", 0)
        replacement_year = self._kwargs.get("replacement_year", self._years_vec[-1])

        cost_escalator = self._kwargs.get("escalator", 0)
        replacement_cost_dollars_year = self._kwargs.get("replacement_cost_dollars_year", 2022)

        replacement_cost = replacement_cost * (
            1 + cost_escalator ** (replacement_year - replacement_cost_dollars_year)
        )

        replacement_cost_vec = [
            replacement_cost if i==replacement_year else 0 for i in self._years_vec
        ]

        return replacement_cost_vec
    
    def _get_replacement_book_value(self) -> List[float]:
        replacement_cost = max(self.replacement_cost)
        replacement_year = self._kwargs.get("replacement_year", self._years_vec[-1])
        replacement_lifetime = self._kwargs.get(
            "replacement_lifetime",
            self._kwargs.get("lifetime", 10)
        )
        salvage_val = 0

        depreciation_rate = (replacement_cost - salvage_val) / replacement_lifetime

        replacement_book_val = [
            max(replacement_cost - depreciation_rate * (i - replacement_year), 0)
            if i >= replacement_year
            else 0
            for i in self._years_vec
        ]

        return replacement_book_val
    
    def _get_cost_table(self) -> pd.DataFrame:
        asset_type = self._kwargs.get("end_use", "domestic_hot_water")

        values = {
            "{}_existing_book_value".format(asset_type): self.existing_book_val,
            "{}_replacement_vec".format(asset_type): np.array(self.replacement_vec, dtype=int),
            "{}_existing_stranded_value".format(asset_type): self.existing_stranded_val,
            "{}_replacement_cost".format(asset_type): self.replacement_cost,
            "{}_replacement_book_val".format(asset_type): self.replacement_book_val,
        }

        cost_table = pd.DataFrame(values, index=self._years_vec)

        return cost_table
