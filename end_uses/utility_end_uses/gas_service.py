"""
Defines Gas Service end use
"""
import numpy as np
from typing import List

from end_uses.utility_end_uses.pipeline import Pipeline


GAS_SHUTOFF_SCENARIOS = ["natural_elec", "accelerated_elec", "hybrid_npa"]
GAS_RETROFIT_SCENARIOS = ["natural_elec", "hybrid_gas", "continued_gas"]
RETROFIT_YEAR = 2025


class GasService(Pipeline):
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
            "gas_service",
        )

        self.replacement_cost = kwargs.get("replacement_cost", 0)
        self.book_value: list = []
        self.shutoff_year: list = []

    def initialize_end_use(self) -> None:
        super().initialize_end_use()
        self.book_value = self.get_book_value()
        self.shutoff_year = self.get_shutoff_year()
        self.stranded_value = self._update_stranded_value()

    #TODO: Here, I think the connected assets would just be a single gas meter
    # (can confirm with MJW that we wouldn't have scenarios of multiple connections)
    # We therefore should use the operational vector of the associated gas meter to understand when
    # the gas service would be shut off in elec and hybrid npa scenarios

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
            shutoff_year_vec = self.connected_assets[0].building._retrofit_vec

        return shutoff_year_vec

    def _update_stranded_value(self) -> List[float]:
        return (np.array(self.book_value) * np.array(self.shutoff_year)).tolist()
