"""
Defines a building. A bucket for all end uses
"""
import json

import numpy as np

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
        aggregate (list): Aggregate attributes across all end-uses at the building
            (Currently just sums install costs for stoves)
        sum_install_costs (list): Sum all install cost vectors across stove end uses
    """
    def __init__(self, building_params: dict, sim_settings: dict):
        self.building_params: dict = building_params
        self.sim_settings: dict = sim_settings

        self.building_id: str = ""
        self.end_uses: dict = {}

    def populate_building(self) -> None:
        """
        Creates instances of all assets for a given building based on the config file
        """
        self._get_building_id()
        self._create_end_uses()

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

    def aggregate(self) -> list:
        """
        Aggregate cost and energy uses across all end-uses at the building
        """
        return self.sum_install_costs()

    def sum_install_costs(self) -> list:
        """
        Sum all install cost vectors across stove end uses
        """
        install_costs = np.zeros(20)
        for stove in self.end_uses["stove"].values():
            install_costs += np.array(stove.install_cost)

        return install_costs.tolist()
