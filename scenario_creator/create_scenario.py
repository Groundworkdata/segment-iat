"""
Creates a scenario based on input values
"""
import json
from typing import List

from buildings.building import Building
from utility_network.utility_network import UtilityNetwork


class ScenarioCreator:
    """
    Create scenario for a parcel and tally total energy usages
    """
    def __init__(
            self,
            sim_settings_filepath: str,
            building_config_filepath: str,
            utility_network_config_filepath: str,
            scenario_mapping_filepath: str
    ):
        self._sim_settings_filepath = sim_settings_filepath
        self._building_config_filepath = building_config_filepath
        self._utility_network_config_filepath = utility_network_config_filepath
        self._scenario_mapping_filepath = scenario_mapping_filepath

        self.sim_config: dict = {}
        self.scenario_mapping: List[dict] = []
        self.buildings_config: dict = {}
        self.buildings: dict = {}
        self.utility_network: UtilityNetwork = None

    def create_scenario(self):
        self.get_sim_settings()
        self.get_scenario_mapping()
        self.create_building()
        # TODO: Update after utility model changes complete
        # self.get_utility_network()

    def get_sim_settings(self) -> None:
        """
        Read in simulation settings
        """
        with open(self._sim_settings_filepath) as f:
            data = json.load(f)
        self.sim_config = data

    def get_scenario_mapping(self) -> None:
        """
        Read in ResStock scenario mapping
        """
        with open(self._scenario_mapping_filepath) as f:
            data = json.load(f)
        self.scenario_mapping = data

    def create_building(self) -> None:
        with open(self._building_config_filepath) as f:
            data = json.load(f)
        self.buildings_config = data

        for building_params in self.buildings_config:
            building = Building(
                building_params,
                self.sim_config,
                self.scenario_mapping
            )

            building.populate_building()
            building.write_building_energy_info()
            building.write_building_cost_info()

            self.buildings[building.building_id] = building

    def get_utility_network(self):
        """
        Create the utility network based on the input config
        """
        self.utility_network = UtilityNetwork(
            self._utility_network_config_filepath,
            self.sim_config,
            self.buildings
        )

        self.utility_network.create_utility_network()
