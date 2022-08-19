"""
Defines a building. A bucket for all end uses
"""
from fileinput import close
import json
from typing import Dict

import numpy as np
import pandas as pd

from end_uses.building_end_uses.stove import Stove


class Building:
    """
    A bucket for all end uses at a parcel. Currently assuming one building/one unit per parcel

    Args:
        building_id (str): The ID of the building
        building_config (str): Filepath of a config file for the building's end uses
        sim_settings (dict): Dict of simulation settings -- {
            sim_start_year (int): The simulation start year
            sim_end_year (int): The simulation end year (exclusive)
        }

    Attributes:
        building_id (str): The ID of the building
        sim_settings (dict): Dict of simulation settings
        building_params (dict): Dict of building input parameters from config file
        end_uses (dict): Dict of building end use class instances

    Methods:
        populate_building (None): Creates building end use class instances
        write_building_cost_info (None): Write building cost information to a CSV
        write_building_energy_info (None): Write building energy information to a CSV
    """
    def __init__(self, building_params: dict, sim_settings: dict):
        self.building_params: dict = building_params
        self.sim_settings: dict = sim_settings

        self._year_timestamps: pd.DatetimeIndex = None
        self.years_vec: list = []
        self.building_id: str = ""
        self.end_uses: dict = {}

    def populate_building(self) -> None:
        """
        Creates instances of all assets for a given building based on the config file
        """
        self._get_years_vec()
        self._get_building_id()
        self._create_end_uses()

    def _get_years_vec(self) -> None:
        self.years_vec = list(range(
            self.sim_settings.get("sim_start_year", 2020),
            self.sim_settings.get("sim_end_year", 2050)
        ))

        self._year_timestamps = pd.date_range(
            start="2018-01-01", end="2019-01-01", freq="H", closed="left"
        )

    def _get_building_id(self):
        self.building_id = self.building_params.get("building_id")

    def _create_end_uses(self):
        """
        Create the end uses for the building
        """
        end_use_params = self.building_params.get("end_uses")

        for end_use_type, end_uses in end_use_params.items():
            if end_use_type not in self.end_uses:
                self.end_uses[end_use_type] = {}

            for end_use in end_uses:
                end_use_id = end_use.get("end_use_id")
                self.end_uses[end_use_type][end_use_id] = self._get_single_end_use(end_use)

    def _get_single_end_use(self, params: dict):
        config_filepath = params.pop("end_use_config")

        with open(config_filepath) as f:
            data = json.load(f)

        end_use_params = data

        if params.get("end_use_type") == "stove":
            stove = Stove(
                **params,
                **end_use_params,
                **self.sim_settings
            )

            stove.initialize_end_use()

            return stove

        return None

    def write_building_cost_info(self) -> None:
        """
        Write calculated building information for total costs
        """
        costs_df = self._sum_end_use_figures("install_cost")
        depreciations_df = self._sum_end_use_figures("depreciation")
        stranded_value_df = self._sum_end_use_figures("stranded_value")

        full_costs_df = pd.merge(costs_df, depreciations_df, left_index=True, right_index=True)
        full_costs_df = pd.merge(
            full_costs_df, stranded_value_df, left_index=True, right_index=True
        )

        full_costs_df.to_csv("./{}_costs.csv".format(self.building_id), index_label="year")

    def write_building_energy_info(self) -> None:
        """
        Write calcualted building information for energy use
        """
        elec_consump_df = self._sum_end_use_figures("elec_consump_annual")
        gas_consump_df = self._sum_end_use_figures("gas_consump_annual")
        elec_peak_consump_df = self._sum_end_use_figures("elec_peak_annual")
        gas_peak_consump_df = self._sum_end_use_figures("gas_peak_annual")

        full_e_df = pd.merge(elec_consump_df, gas_consump_df, left_index=True, right_index=True)
        full_e_df = pd.merge(full_e_df, elec_peak_consump_df, left_index=True, right_index=True)
        full_e_df = pd.merge(full_e_df, gas_peak_consump_df, left_index=True, right_index=True)

        full_e_df.to_csv("./{}_energy.csv".format(self.building_id), index_label="year")

        total_consump_ts = self.get_total_consumption("elec")
        total_consump_ts.to_csv(
            "./{}_total_elec_consump.csv".format(self.building_id),
            index_label="timestamp"
        )

    def _sum_end_use_figures(self, cost_figure) -> pd.DataFrame:
        """
        cost_figure must be in [
            "install_cost", "depreciation", "stranded_value",
            "elec_consump_annual", "gas_consump_annual", "elec_peak_annual", "gas_peak_annual"
        ]
        """
        costs = {}

        stoves = self.end_uses.get("stove")

        for stove_id, stove in stoves.items():
            costs[stove_id + "_{}".format(cost_figure)] = getattr(stove, cost_figure)

        costs_df = pd.DataFrame(costs)
        costs_df.index = self.years_vec

        costs_df["total_{}".format(cost_figure)] = costs_df.sum(axis=1)

        return costs_df

    def get_total_consumption(self, e_type) -> pd.DataFrame:
        """
        Get the total energy consumption at the building, summing all end uses

        e_type must be in ["elec", "gas"]
        """
        total_consump = {}

        stoves = self.end_uses.get("stove")

        # TODO: This wil output the elec timeseries for every asset, regardless of install year
        # But what we really want to see is the impact the asset replacement has on load
        # So do we want this to be an 8760 X number of sim years? That becomes a lot more data to
        # save and track than just 8760 datapoints per building

        for stove_id, stove in stoves.items():
            total_consump[stove_id] = getattr(stove, "{}_consump".format(e_type))

        total_consump_df = pd.DataFrame(total_consump)
        total_consump_df.index = self._year_timestamps

        return total_consump_df
