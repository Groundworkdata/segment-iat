"""
Creates a scenario based on input values
"""
import json

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
            utility_network_config_filepath: str
    ):
        self._sim_settings_filepath = sim_settings_filepath
        self._building_config_filepath = building_config_filepath
        self._utility_network_config_filepath = utility_network_config_filepath

        self.sim_config: dict = {}
        self.building_config: dict = {}
        self.buildings: dict = {}
        self.utility_network: UtilityNetwork = None

    def create_scenario(self):
        self.get_sim_settings()
        self.create_building()
        self.get_utility_network()

    def get_sim_settings(self) -> None:
        """
        Read in simulation settings
        """
        with open(self._sim_settings_filepath) as f:
            data = json.load(f)
        self.sim_config = data

    def create_building(self) -> None:
        # TODO: Add ability for multiple buildings
        building = Building(
            "building001",
            self._building_config_filepath,
            self.sim_config
        )

        building.populate_building()
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
