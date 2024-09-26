"""
BuildingMeasure parent class
"""
from typing import List

import numpy as np
import pandas as pd


DEFAULT_INFLATION_RATE = 0.02
DEFAULT_COST_YEAR = 2022


class BuildingMeasure:
    """
    Defines the parent BuildingMeasure class for all building-level measures

    Args:
        years_vec (List[int]): List of simulation years
        incentive_data (List[dict]): Applicable incentives for the measure
        energy_keys (List[str]): Key names of energy fields for the Measure
        lifetime (int): The measure lifetime, in years
        custom_baseline_energy (pd.DataFrame): Custom input timeseries of baseline energy consump
        custom_retrofit_energy (pd.DataFrame): Custom input timeseries of retrofit energy consump

    Keyword Args:
        install_year (int): The install year of the asset
        asset_cost (float): The cost of the asset in present day dollars
            (or in $ from install year if installed prior to sim start)
        replacement_year (int): The replacement year of the asset
        sim_start_year (int): The simulation start year
        sim_end_year (int): The simulation end year (exclusive)
        elec_consump (float): The total annual elec consump, in kWh
        gas_consump (float): The total annual gas consump, in kWh
        building_id (str): Identifies the building where the end use is located

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
        elec_consump (Dict[str, float]): Timeseries elec consump of the end use for one year, in kWh
        gas_consump (Dict[str, float]): Timeseries gas consump of the end use for one year, in kWh
        elec_consump_annual (list): The total annual elec consump of the end use, in kWh
        gas_consump_annual (list): The total annual gas consump of the end use, in kWh
        elec_peak_annual (list): Annual peak elec consump, in kW
        gas_peak_annual (list): Annual peak gas consump, in kW
        gas_leakage (list): List of annual gas leakage from end use, in kWh
        building_id (str): Identifies the building where the end use is located

    Methods:
        initialize_end_use (None): Performs all calculations for the end use
    """
    def __init__(
            self,
            years_vec: List[int],
            incentive_data: List[dict],
            energy_keys: List[str],
            lifetime: int,
            custom_baseline_energy: pd.DataFrame = pd.DataFrame(),
            custom_retrofit_energy: pd.DataFrame = pd.DataFrame(),
            **kwargs
    ):
        self._kwargs = kwargs

        self._years_vec: List[int] = years_vec
        self._incentive_data: List[dict] = incentive_data
        self._energy_keys: List[str] = energy_keys
        self.lifetime: int = lifetime
        self.retrofit_item: str = self._kwargs.get("end_use_retrofit_item")
        self._custom_baseline_energy: pd.DataFrame = custom_baseline_energy
        self._custom_retrofit_energy: pd.DataFrame = custom_retrofit_energy

        self.existing_book_val: List[float] = []
        self._replacement_vec: List[bool] = []
        self.existing_stranded_val: List[float] = []
        self.replacement_cost_gross: float = 0
        self.replacement_cost_gross_vec: List[float] = []
        self.incentives: List[dict] = []
        self.total_incentive_value: float = 0
        self.total_incentive_vec: List[float] = 0
        self.replacement_cost_net: float = 0
        self.replacement_cost_net_vec: List[float] = []
        self.replacement_book_val: List[float] = []
        self.cost_table: pd.DataFrame = None

        self.baseline_energy_use = None
        self.retrofit_energy_use = None

    def initialize_end_use(self) -> None:
        """
        Initialize the end use and calculate values
        """
        self.existing_book_val = self._get_existing_book_val()
        self._replacement_vec = self._get_replacement_vec()
        self.existing_stranded_val = self._get_existing_stranded_val()
        self.replacement_cost_gross = self._get_replacement_cost_gross_value()
        self.replacement_cost_gross_vec = self._get_replacement_cost_gross_vec()
        self.incentives = self._get_incentives()
        self.total_incentive_value = self._get_total_incentive_value()
        self.total_incentive_vec = self._get_total_incentive_vec()
        self.replacement_cost_net = self._get_replacement_cost_net()
        self.replacement_cost_net_vec = self._get_replacement_cost_net_vec()
        self.replacement_book_val = self._get_replacement_book_value()
        self.cost_table = self._get_cost_table()

        if not self._custom_baseline_energy.empty and not self._custom_retrofit_energy.empty:
            self._get_custom_energies()

    def _get_custom_energies(self) -> None:
        self.baseline_energy_use = self._custom_baseline_energy.reindex(
            self._energy_keys, axis=1, fill_value=0
        )

        self.retrofit_energy_use = self._custom_retrofit_energy.reindex(
            self._energy_keys, axis=1, fill_value=0
        )

    def _get_existing_book_val(self) -> List[float]:
        existing_install_year = self._kwargs.get("existing_install_year", self._years_vec[0])
        existing_cost_dollars_year = self._kwargs.get("replacement_cost_dollars_year", DEFAULT_COST_YEAR)
        cost_escalator = self._kwargs.get("inflation_escalator", DEFAULT_INFLATION_RATE)
        existing_install_cost = self._kwargs.get("existing_install_cost", 0)
        salvage_val = 0

        existing_adjusted_cost = existing_install_cost * (
            (1 - cost_escalator) ** (existing_cost_dollars_year - existing_install_year)
        )

        depreciation_rate = (existing_adjusted_cost - salvage_val) / self.lifetime

        existing_book_val = [
            max(existing_adjusted_cost - depreciation_rate * (i - existing_install_year), 0)
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
        stranded_val = np.multiply(self.existing_book_val, self._replacement_vec).tolist()
        return stranded_val

    def _get_replacement_cost_gross_value(self) -> float:
        """
        Get the gross replacement cost (before incentives)
        """
        replacement_cost = self._kwargs.get("replacement_cost", 0)
        replacement_year = self._kwargs.get("replacement_year", self._years_vec[-1])

        cost_escalator = self._kwargs.get("inflation_escalator", DEFAULT_INFLATION_RATE)
        replacement_cost_dollars_year = self._kwargs.get("replacement_cost_dollars_year", DEFAULT_COST_YEAR)

        replacement_cost = replacement_cost * (
            (1 + cost_escalator) ** (replacement_year - replacement_cost_dollars_year)
        )

        return replacement_cost

    def _get_replacement_cost_gross_vec(self) -> List[float]:
        replacement_year = self._kwargs.get("replacement_year", self._years_vec[-1])

        replacement_cost_vec = [
            self.replacement_cost_gross if i==replacement_year else 0 for i in self._years_vec
        ]

        return replacement_cost_vec

    def _get_incentives(self) -> List[dict]:
        """
        Get the incentive amounts for this measure over the Study timeframe
        """
        replacement_year = self._kwargs.get("replacement_year", self._years_vec[-1])

        incentives = []
        for i in self._incentive_data:
            if self.retrofit_item in i["items"]:
                amount_data = i["amount"]

                incentive_amount = 0
                if amount_data["type"] == "dollar_amount":
                    incentive_amount = amount_data["number"]
                elif amount_data["type"] == "percent":
                    incentive_amount = amount_data["number"] * self.replacement_cost_gross

                incentive_amount = max(incentive_amount, amount_data.get("maximum", 0))

                incentive_amount = incentive_amount * (replacement_year >= i["start_date"])
                incentive_amount = incentive_amount * (replacement_year < i["end_date"])

                incentives.append({
                    "authority_type": i["authority_type"],
                    "program": i["program"],
                    "asset_type": self._kwargs.get("end_use"),
                    "items": i["items"],
                    "upfront_cost": self.replacement_cost_gross,
                    "incentive_amount": incentive_amount,
                    "start_date": i["start_date"],
                    "end_date": i["end_date"],
                    "install_year": replacement_year
                })

        if not incentives:
            incentives.append({
                "authority_type": None,
                "program": None,
                "asset_type": None,
                "items": None,
                "upfront_costs": 0,
                "incentive_amount": 0,
                "start_date": None,
                "end_date": None,
                "install_year": None
            })

        return incentives
    
    def _get_total_incentive_value(self) -> float:
        """
        Sum all incentive values in self.incentives
        """
        return sum([i["incentive_amount"] for i in self.incentives])
    
    def _get_total_incentive_vec(self) -> List[float]:
        """
        Vector of total incentive value over the Study timeframe
        """
        return np.multiply(self._replacement_vec, self.total_incentive_value).tolist()
    
    def _get_replacement_cost_net(self) -> float:
        """
        Gross replacement cost minus total incentive value
        """
        return self.replacement_cost_gross - self.total_incentive_value
    
    def _get_replacement_cost_net_vec(self) -> List[float]:
        """
        Net replacement cost (gross minus incentive) over the Study timeframe
        """
        return np.multiply(self._replacement_vec, self.replacement_cost_net).tolist()

    def _get_replacement_book_value(self) -> List[float]:
        """
        Book value of the replacement measure, using the net replacement cost
        """
        replacement_year = self._kwargs.get("replacement_year", self._years_vec[-1])
        salvage_val = 0

        depreciation_rate = (self.replacement_cost_net - salvage_val) / self.lifetime

        replacement_book_val = [
            max(self.replacement_cost_net - depreciation_rate * (i - replacement_year), 0)
            if i >= replacement_year
            else 0
            for i in self._years_vec
        ]

        return replacement_book_val

    #FIXME: Not in use
    def _get_cost_table(self) -> pd.DataFrame:
        asset_type = self._kwargs.get("end_use")

        values = {
            "{}_existing_book_value".format(asset_type): self.existing_book_val,
            "{}_replacement_vec".format(asset_type): np.array(self._replacement_vec, dtype=int),
            "{}_existing_stranded_value".format(asset_type): self.existing_stranded_val,
            "{}_replacement_cost".format(asset_type): self.replacement_cost_gross_vec,
            "{}_replacement_book_val".format(asset_type): self.replacement_book_val,
        }

        cost_table = pd.DataFrame(values, index=self._years_vec)

        return cost_table
