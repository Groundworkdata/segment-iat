"""
Creates a scenario based on input values
"""
import json

from buildings.building import Building
from end_uses.meters.elec_meter import ElecMeter
from end_uses.meters.gas_meter import GasMeter


class ScenarioCreator:
    """
    Create scenario for a parcel and tally total energy usages
    """
    def __init__(
            self,
            sim_settings_filepath: str,
            building_config_filepath: str
    ):
        self._sim_settings_filepath = sim_settings_filepath
        self._building_config_filepath = building_config_filepath

        self.sim_config: dict = {}
        self.building_config: dict = {}
        self.buildings: list = []
        self.end_uses: list = []
        self.meters: list = []

    def create_scenario(self):
        self.get_sim_settings()
        self.create_building()
        self.get_meters()

    def get_sim_settings(self) -> None:
        """
        Read in simulation settings
        """
        with open(self._sim_settings_filepath) as f:
            data = json.load(f)
        self.sim_config = data

    def create_building(self) -> None:
        building = Building(
            "building1",
            self._building_config_filepath,
            self.sim_config
        )

        building.populate_building()
        self.buildings.append(building)

    def get_meters(self):
        self.get_elec_meter()
        self.get_gas_meter()

    def get_elec_meter(self):
        # TODO: Config files for utility assets (meters, etc)
        elec_meter = ElecMeter(
            2020,
            100,
            2050,
            30,
            2020,
            2040,
            "asset_id",
            "parent_id",
            self.end_uses
        )

        elec_meter.initialize_meter()
        self.meters.append(elec_meter)

    def get_gas_meter(self):
        gas_meter = GasMeter(
            2020,
            100,
            2050,
            30,
            2020,
            2040,
            "asset_id",
            "parent_id",
            self.end_uses
        )

        gas_meter.initialize_meter()
        self.meters.append(gas_meter)
