"""
Creates a scenario based on input values
"""
import numpy as np
import pandas as pd

from buildings.building import Building
from end_uses.meters.elec_meter import ElecMeter
from end_uses.meters.gas_meter import GasMeter


class ScenarioCreator:
    """
    Create scenario for a parcel and tally total energy usages
    """
    def __init__(
            self,
            building_config_filepath: str
    ):
        self._building_config_filepath = building_config_filepath

        self.building_config: dict = {}
        self.buildings: list = []
        self.end_uses: list = []
        self.meters: list = []

    def create_scenario(self):
        self.create_building()
        self.get_meters()

    def read_building_config(self) -> None:
        building_df = pd.read_json(self._building_config_filepath)
        self.building_config = building_df.to_dict()

    def create_building(self) -> None:
        # building = Building("building1", self.building_config)
        building = Building("building1", self._building_config_filepath)
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
