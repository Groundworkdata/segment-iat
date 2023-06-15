"""
Defines Mains end use
"""
import numpy as np
import pandas as pd
from typing import List
import warnings

from end_uses.utility_end_uses.pipeline import Pipeline


GAS_SHUTOFF_SCENARIOS = ["natural_elec", "accelerated_elec", "hybrid_npa"]
GAS_RETROFIT_SCENARIOS = ["natural_elec", "hybrid_gas", "continued_gas", "hybrid_gas_immediate"]
RETROFIT_YEAR = 2025
ANNUAL_OM_FILEPATH = "./config_files/operating_expenses/gas_operating_expenses.csv"


#TODO: Write unit tests
class GasMain(Pipeline):
    def __init__(self, **kwargs):
        super().__init__(
            kwargs.get("gisid"),
            kwargs.get("parentid"),
            kwargs.get("inst_date"),
            kwargs.get("inst_cost"),
            kwargs.get("lifetime"),
            kwargs.get("sim_start_year"),
            kwargs.get("sim_end_year"),
            kwargs.get("replacement_year"),
            kwargs.get("decarb_scenario"),
            kwargs.get("length_ft"),
            kwargs.get("pressure"),
            kwargs.get("diameter"),
            kwargs.get("material"),
            kwargs.get("connected_assets"),
            "gas_main",
        )

        self.replacement_cost = kwargs.get("replacement_cost", 0)
        self.shutoff_cost = kwargs.get("shutoff_cost", 0)
        self.book_value: list = []
        self.shutoff_year: list = []

    def initialize_end_use(self) -> None:
        super().initialize_end_use()
        self.book_value = self.get_book_value()
        self.shutoff_year = self.get_shutoff_year()
        self.stranded_value = self._update_stranded_value()
        self.annual_operating_expenses = self._get_annual_om()

    def get_operational_vector(self) -> list:
        operational_vecs = []

        operational_vector = np.zeros(len(self.years_vector))
        operational_vecs.append(operational_vector)

        for asset in self.connected_assets:
            operational_vecs.append(np.array(asset.operational_vector))

        operational_vector = np.stack(operational_vecs).max(axis=0)

        return operational_vector.tolist()
    
    def _get_replacement_vec(self) -> List[bool]:
        replacement_vec = [False] * len(self.years_vector)
        if self.decarb_scenario in GAS_RETROFIT_SCENARIOS:
            replacement_vec[RETROFIT_YEAR - self.sim_start_year] = True

        return replacement_vec

    def get_retrofit_vector(self) -> list:
        retrofit_vector = np.zeros(len(self.years_vector))
        if self.decarb_scenario in GAS_RETROFIT_SCENARIOS:
            retrofit_vector[RETROFIT_YEAR - self.sim_start_year:] = 1

        return retrofit_vector.astype(bool).tolist()

    #TODO: Rename - install_cost is misleading. This is more of a retrofit or capital cost vector
    def get_install_cost(self) -> list:
        install_cost = np.zeros(len(self.years_vector))

        if self.decarb_scenario in GAS_RETROFIT_SCENARIOS:
            install_cost[RETROFIT_YEAR - self.sim_start_year] = self.replacement_cost

        return install_cost.tolist()

    def get_depreciation(self) -> List[float]:
        depreciation = np.zeros(len(self.years_vector))

        if self.decarb_scenario in GAS_RETROFIT_SCENARIOS:
            depreciation_rate = self.replacement_cost / self.lifetime
            depreciation[RETROFIT_YEAR - self.sim_start_year:] = [
                max(self.replacement_cost - depreciation_rate * i, 0)
                for i in range(self.sim_end_year - RETROFIT_YEAR)
            ]

        return depreciation.tolist()

    def get_book_value(self) -> List[float]:
        return self.depreciation

    def get_shutoff_year(self) -> List[float]:
        shutoff_year_vec = [0] * len(self.years_vector)

        if self.decarb_scenario in GAS_SHUTOFF_SCENARIOS:
            shutoff_year = 0
            for service in self.connected_assets:
                building = service.connected_assets[0].building

                for idx, retrofit in enumerate(building._retrofit_vec):
                    if retrofit:
                        shutoff_year = max(shutoff_year, idx)

            if shutoff_year:
                shutoff_year_vec[shutoff_year] = 1

        return shutoff_year_vec

    def _update_stranded_value(self) -> List[float]:
        return (np.array(self.book_value) * np.array(self.shutoff_year)).tolist()
    
    def get_system_shutoff_cost(self) -> List[float]:
        return (np.array(self.shutoff_year) * self.shutoff_cost).tolist()

    def _get_annual_om(self) -> List[float]:
        om_table = pd.read_csv(ANNUAL_OM_FILEPATH, index_col="material").to_dict(orient="index")

        if self.material not in om_table.keys():
            warnings.warn(f"Material {self.material} not in O&M table! Using $0 / year.")
        
        annual_operating_expense = om_table.get(self.material, {}).get(
            "operating_expense_per_mile", 0
        )

        # Convert length in feet to miles
        annual_operating_expense = annual_operating_expense * (self.length / 5280)

        return (annual_operating_expense * np.array(self.operational_vector)).tolist()
