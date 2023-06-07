"""
Defines Gas Service end use
"""
from typing import Dict
import pandas as pd
import numpy as np

from end_uses.utility_end_uses.utility_end_use import UtilityEndUse
from collections import Counter


class ElecTransformer(UtilityEndUse):
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
        )

        self.decarb_scenario = (kwargs.get("decarb_scenario"),)
        self.circuit: int = kwargs.get("circuit")
        self.trans_qty: int = kwargs.get("trans_qty")
        self.tr_secvolt: str = kwargs.get("tr_secvolt")
        self.PolePadVLT: str = kwargs.get("PolePadVLT")
        self._bank_kva: int = kwargs.get("bank_KVA")

        self.connected_assets: list = kwargs.get("connected_assets")

        self.annual_bank_KVA: list = []
        self.annual_total_energy_use: dict = []
        self.annual_peak_energy_use: list = []
        self.annual_energy_use_timeseries: dict = []

        self.required_upgrade_year: int = 0
        self.upgrade_cost: list = []
        self.overloading_flag: list = []
        self.overloading_ratio: list = []

    def initialize_end_use(self) -> None:
        """
        Calculates aggregate consumption values behind the meter
        """
        super().initialize_end_use()
        if self.connected_assets:
            self.annual_bank_KVA = self._get_annual_bank_kva()
            self.annual_total_energy_use = self.get_annual_total_energy_use()
            self.annual_energy_use_timeseries = self.get_annual_energy_use_timeseries()
            self.annual_peak_energy_use = self.get_annual_peak_energy_use()
            self.required_upgrade_year = self.get_upgrade_year()
            self.is_replacement_vector = self.update_is_replacement_vector()
            self.retrofit_vector = self.update_retrofit_vector()
            self.upgrade_cost = self.get_upgrade_cost()
            self.get_overloading_status()

    def _get_annual_bank_kva(self) -> list:
        """
        Return the bank KVA for each year
        """
        return [self._bank_kva] * len(self.years_vector)

    def get_annual_total_energy_use(self) -> dict:
        """
        Get the total energy use on a gas service lines

        Returns:
            list: List of annual energy consumption
        """
        tmp_counter = Counter()
        for meter in self.connected_assets:
            tmp_counter.update(meter.annual_total_energy_use)

        return dict(tmp_counter)

    def get_annual_energy_use_timeseries(self) -> Dict[int, pd.Series]:
        energy_timeseries = {i: pd.Series(0, index=self.year_timestamps) for i in self.years_vector}
        for i in self.years_vector:
            for meter in self.connected_assets:
                energy_timeseries[i] += meter.annual_energy_use_timeseries[i]

        return energy_timeseries

    def get_annual_peak_energy_use(self) -> list:
        annual_peak = []

        for i in self.years_vector:
            annual_peak.append(self.annual_energy_use_timeseries[i].max())

        return annual_peak
    
    def get_upgrade_year(self) -> int:
        """
        If we exceed the transformer capacity, return the year where this happens. Also, update the
        total bank_KVA to account for this upgrade

        NOTE: This is limited to upgrading the transformer ONCE and it doubles the transformer
        capacity. Therefore, if the load reaches over 2x the transformer capacity, this function
        will not account for that.
        """
        for years, load in zip(enumerate(self.years_vector), self.annual_peak_energy_use):
            year_idx = years[0]
            year = years[1]

            if load > self.annual_bank_KVA[year_idx] * 1000:
                #TODO: Refactor. Kind of ugly
                bank_kva = np.array(self.annual_bank_KVA)
                bank_kva[year_idx:] *= 2
                self.annual_bank_KVA = bank_kva.tolist()
                return year
        return 0
    
    def update_is_replacement_vector(self) -> list:
        retrofit_vector = np.zeros(len(self.years_vector))
        if self.required_upgrade_year:
            retrofit_vector[self.required_upgrade_year - self.sim_start_year:] = 1

        return retrofit_vector.astype(bool).tolist()
    
    def update_retrofit_vector(self) -> list:
        retrofit_vector = np.zeros(len(self.years_vector))
        if self.required_upgrade_year:
            retrofit_vector[self.required_upgrade_year - self.sim_start_year] = 1

        return retrofit_vector.astype(bool).tolist()

    def get_upgrade_cost(self) -> list:
        upgrade_cost = np.zeros(len(self.years_vector))

        if self.required_upgrade_year:
            #FIXME: Placeholder upgrade cost
            upgrade_cost[self.required_upgrade_year - self.sim_start_year] = 2000

        return upgrade_cost.tolist()

    def get_overloading_status(self) -> None:
        self.overloading_flag = (
            np.array(self.annual_peak_energy_use) > (np.array(self.annual_bank_KVA) * 1000)
        ).astype(int).tolist()

        self.overloading_ratio = (
            np.array(self.annual_peak_energy_use) / (np.array(self.annual_bank_KVA) * 1000)
        ).tolist()
