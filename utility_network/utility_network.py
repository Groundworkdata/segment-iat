"""
Defines a utility network. A bucket for all utility assets
"""
from typing import List, Dict

import json

from buildings.building import Building
from end_uses.utility_end_uses.gas_main import GasMain
from end_uses.utility_end_uses.gas_service import GasService
from end_uses.meters.gas_meter import GasMeter
from end_uses.meters.elec_meter import ElecMeter


class UtilityNetwork:
    """
    A bucket for all utility assets. Currently assuming one main line and one service line per
    network

    Args:
        network_config_filepath (str): Filepath to utility network config file
        sim_settings (dict): Dict of simulation settings -- {
            sim_start_year (int): The simulation start year
            sim_end_year (int): The simulation end year (exclusive)
        }
        buildings (Dict[str, Building]): Dict of Building instances in the scenario -- {
            building_id: Building,
            ...
        }

    Attributes:
        sim_settings (dict): Dict of simulation settings
        network_config (dict): Dict of utility network configuration
        gas_main (GasMain): The GasMain object
        gas_services (List[GasService]): List of GasService objects for all service lines
        gas_meters (List[GasMeter]): List of GasMeter objects for all gas meters
        elec_meters (List[ElecMeter]): List of ElecMeter objects for all elec meters

    Methods:
        create_utility_network (None): Creates the utility network modules based on the input config
    """
    def __init__(
            self,
            network_config_filepath: str,
            sim_settings: dict,
            buildings: Dict[str, Building]
    ):
        self._network_config_filepath = network_config_filepath

        self.sim_settings = sim_settings
        self.buildings = buildings
        self.network_config: dict = {}

        self.gas_main: GasMain = None
        self.gas_services: List[GasService] = []
        self.gas_meters: List[GasMeter] = []
        self.elec_meters: List[ElecMeter] = []

    def create_utility_network(self) -> None:
        """
        Calls all functions to populate the utility network
        """
        self._read_config()
        self._get_gas_mains()
        self._get_gas_services()
        self._get_gas_meters()
        self._get_elec_meters()

    def _read_config(self) -> None:
        """
        Read in the utilty network config file and save to network_config attr
        """
        with open(self._network_config_filepath) as f:
            data = json.load(f)

        self.network_config = data

    def _get_gas_mains(self) -> None:
        """
        Instantiate the GasMain and write to gas_main attr
        """
        main_config = self.network_config.get("gas_main")
        self.gas_main = GasMain(**main_config, **self.sim_settings)

    def _get_gas_services(self) -> None:
        """
        Instantiate all necessary GasService instances and save to gas_services list attr
        """
        services_config = self.network_config.get("gas_services")
        for service in services_config:
            self.gas_services.append(GasService(**service, **self.sim_settings))

    def _get_gas_meters(self) -> None:
        """
        Instantiate all necessary GasMeter instances and save to gas_meters list attr
        """
        gas_meter_config = self.network_config.get("gas_meters")
        for meter_config in gas_meter_config:
            building_id = meter_config.get("building_id")
            building = self.buildings.get(building_id)

            gas_meter = GasMeter(**meter_config, **self.sim_settings, building=building)
            gas_meter.initialize_end_use()
            self.gas_meters.append(gas_meter)

    def _get_elec_meters(self) -> None:
        """
        Instantiate all necessary ElecMeter instances and save to elec_meters list attr
        """
        elec_meter_config = self.network_config.get("elec_meters")
        for meter_config in elec_meter_config:
            building_id = meter_config.get("building_id")
            building = self.buildings.get(building_id)

            elec_meter = ElecMeter(**meter_config, **self.sim_settings, building=building)
            elec_meter.initialize_end_use()
            self.elec_meters.append(elec_meter)
