"""
Defines Gas Service end use
"""
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
        self.bank_KVA: int = kwargs.get("bank_KVA")
        self.PolePadVLT: str = kwargs.get("PolePadVLT")

        self.connected_assets: list = kwargs.get("connected_assets")

        self.annual_total_energy_use: dict = []
        self.annual_peak_energy_use: dict = []
        self.annual_energy_use_timeseries: dict = []

        self.overloading_flag: dict = []
        self.overloading_ratio: dict = []

    def initialize_end_use(self) -> None:
        """
        Calculates aggregate consumption values behind the meter
        """
        super().initialize_end_use()
        if self.connected_assets:
            self.annual_total_energy_use = self.get_annual_total_energy_use()
            self.annual_peak_energy_use = self.get_annual_peak_energy_use()
            self.annual_energy_use_timeseries = self.get_annual_energy_use_timeseries()
            self.get_overloading_status()

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

    def get_annual_peak_energy_use(self) -> dict:
        tmp_counter = Counter()
        for meter in self.connected_assets:
            tmp_counter.update(meter.annual_peak_energy_use)
        return dict(tmp_counter)

    def get_overloading_status(self) -> dict:

        self.overloading_flag = dict(
            (k, 1 if v > self.bank_KVA * 1000 else 0)
            for k, v in self.annual_peak_energy_use.items()
        )
        self.overloading_ratio = dict(
            (k, v / (self.bank_KVA * 1000))
            for k, v in self.annual_peak_energy_use.items()
        )

    def get_annual_energy_use_timeseries(self) -> list:
        tmp_counter = Counter()
        # for meter in self.connected_assets:
        #     print(meter.annual_energy_use_timeseries)
        # TODO: Add aggregation of timeseries consumption
        # tmp_counter.update(meter.annual_total_energy_use)

        return dict(tmp_counter)
