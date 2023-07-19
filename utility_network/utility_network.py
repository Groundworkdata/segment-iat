"""
Defines a utility network and instantiates all related classes for utility assets
"""
from typing import List, Dict
import pandas as pd

import json

from buildings.building import Building
from end_uses.utility_end_uses.gas_main import GasMain
from end_uses.utility_end_uses.gas_service import GasService
from end_uses.meters.gas_meter import GasMeter

from end_uses.utility_end_uses.elec_service import ElecService
from end_uses.utility_end_uses.elec_secondary import ElecSecondary
from end_uses.utility_end_uses.elec_transformer import ElecTransformer
from end_uses.utility_end_uses.elec_primary import ElecPrimary
from end_uses.meters.elec_meter import ElecMeter


class UtilityNetwork:
    """
    Defines the utility network as an aggregation of discrete utility assets

    Args:
        network_config_filepath (str): Filepath to utility network config file
        sim_settings (dict): Dict of simulation settings
        buildings (Dict[str, Building]): Dict of Building instances in the scenario, organized by id

    Attributes:
        buildings (Dict[str, Building]): Dict of Building instances in the scenario, organized by id
        years_vec (list): List of years in the simulation
        gas_main (List[GasMain]): List of GasMain assets
        gas_services (List[GasService]): List of GasService objects for all service lines
        gas_meters (List[GasMeter]): List of GasMeter objects for all gas meters
        elec_meters (List[ElecMeter]): List of ElecMeter objects for all elec meters
        elec_services (List[ElecService]): List of all ElecService assets
        elec_secondaries (List[ElecSecondary]): List of all ElecSecondary assets
        elec_transformers (List[ElecTransformer]): List of all ElecTransformer assets
        elec_primaries (List[ElecPrimary]): List of all ElecPrimary assets

    Methods:
        populate_utility_network (None): Creates the utility network and associated assets
    """

    def __init__(
        self,
        network_config_filepath: str,
        sim_settings: dict,
        buildings: Dict[str, Building],
    ):
        self._network_config_filepath: str = network_config_filepath
        self._sim_settings: dict = sim_settings
        self.buildings: Dict[str, Building] = buildings

        self._network_config: dict = {}
        self._year_timestamps: pd.DatetimeIndex = None
        self.years_vec: list = []

        self.gas_mains: List[GasMain] = []
        self.gas_services: List[GasService] = []
        self.gas_meters: List[GasMeter] = []
        self.elec_meters: List[ElecMeter] = []
        self.elec_services: List[ElecService] = []
        self.elec_secondaries: List[ElecSecondary] = []
        self.elec_transformers: List[ElecTransformer] = []
        self.elec_primaries: List[ElecPrimary] = []

    def populate_utility_network(self) -> None:
        """
        Calls all functions to populate the utility network
        """
        self._network_config = self._read_json_config(
            config_file_path=self._network_config_filepath
        )

        self._get_years_vec()

        # order is important
        self._create_gas_meters()
        self._create_gas_services()
        self._create_gas_mains()

        self._create_elec_meters()
        self._create_elec_services()
        self._create_elec_secondaries()
        self._create_elec_transformers()
        self._create_elec_primaries()

    def _read_csv_config(self, config_file_path=None) -> None:
        """
        Read in the utilty network config file and save to network_config attr
        """
        data = pd.read_csv(config_file_path)
        return data

    def _read_json_config(self, config_file_path=None) -> None:
        """
        Read in the utilty network config file and save to network_config attr
        """
        with open(config_file_path) as f:
            data = json.load(f)[0]
        return data

    def _get_years_vec(self) -> None:
        """
        Vector of simulation years
        """
        start_year = self._sim_settings.get("sim_start_year", 2021)
        end_year = self._sim_settings.get("sim_end_year", 2050)
        self.years_vec = list(range(start_year, end_year + 1))

        self._year_timestamps = pd.date_range(
            start="{}-01-01".format(start_year),
            end="{}-01-01".format(start_year + 1),
            freq="H",
            inclusive="left",
        )

    def _create_gas_meters(self) -> None:
        """
        Instantiate all necessary GasMeter instances and save to gas_meters list attr
        """
        meter_config_file = self._network_config["networks"]["gas"]["meter_config"]
        meter_configs = self._read_csv_config(config_file_path=meter_config_file)

        for _, meter_config in meter_configs.iterrows():
            building_id = meter_config["LOC_ID"]
            building = self.buildings.get(building_id, None)
            gas_meter = GasMeter(**meter_config, **self._sim_settings, building=building)
            gas_meter.initialize_end_use()
            self.gas_meters.append(gas_meter)

    def _get_children(self, parent_id=None, all_children=None) -> List:
        selected_children = []
        for child in all_children:
            if child.parent_id == parent_id:
                selected_children.append(child)
        return selected_children

    def _create_gas_services(self) -> None:
        """
        Instantiate all necessary GasService instances and save to gas_services list attr
        """
        service_config_file = self._network_config["networks"]["gas"]["service_config"]
        service_configs = self._read_csv_config(config_file_path=service_config_file)
        for _, service_config in service_configs.iterrows():
            connected_meters = self._get_children(
                parent_id=service_config["gisid"], all_children=self.gas_meters
            )

            gas_service = GasService(
                **service_config, **self._sim_settings, connected_assets=connected_meters
            )

            gas_service.initialize_end_use()
            self.gas_services.append(gas_service)

    def _create_gas_mains(self) -> None:
        """
        Instantiate the GasMain and write to gas_main attr
        """
        main_config_file = self._network_config["networks"]["gas"]["mains_config"]
        main_configs = self._read_csv_config(config_file_path=main_config_file)
        for _, main_config in main_configs.iterrows():

            connected_services = self._get_children(
                parent_id=main_config["gisid"], all_children=self.gas_services
            )

            gas_main = GasMain(
                **main_config, **self._sim_settings, connected_assets=connected_services
            )

            gas_main.initialize_end_use()
            self.gas_mains.append(gas_main)

    def _create_elec_meters(self) -> None:
        """
        Instantiate all necessary ElecMeter instances and save to gas_meters list attr
        """
        meter_config_file = self._network_config["networks"]["elec"]["meter_config"]
        meter_configs = self._read_csv_config(config_file_path=meter_config_file)

        for _, meter_config in meter_configs.iterrows():
            building_id = meter_config["LOC_ID"]
            building = self.buildings.get(building_id, None)
            elec_meter = ElecMeter(
                **meter_config, **self._sim_settings, building=building
            )
            elec_meter.initialize_end_use()
            self.elec_meters.append(elec_meter)

    def _create_elec_services(self) -> None:
        """
        Instantiate all necessary ElecService instances and save to gas_services list attr
        """
        service_config_file = self._network_config["networks"]["elec"]["service_config"]
        service_configs = self._read_csv_config(config_file_path=service_config_file)
        for _, service_config in service_configs.iterrows():
            connected_meters = self._get_children(
                parent_id=service_config["gisid"], all_children=self.elec_meters
            )

            elec_service = ElecService(
                **service_config, **self._sim_settings, connected_assets=connected_meters
            )

            elec_service.initialize_end_use()
            self.elec_services.append(elec_service)

    def _create_elec_secondaries(self) -> None:
        """
        Instantiate all necessary ElecSecondaries instances and save to gas_services list attr
        """
        secondary_config_file = self._network_config["networks"]["elec"][
            "secondary_config"
        ]
        secondary_configs = self._read_csv_config(
            config_file_path=secondary_config_file
        )
        for _, secondary_config in secondary_configs.iterrows():
            connected_services = self._get_children(
                parent_id=secondary_config["gisid"], all_children=self.elec_services
            )

            elec_secondary = ElecSecondary(
                **secondary_config,
                **self._sim_settings,
                connected_assets=connected_services
            )

            elec_secondary.initialize_end_use()
            self.elec_secondaries.append(elec_secondary)

    def _create_elec_transformers(self) -> None:
        """
        Instantiate all necessary ElecSecondaries instances and save to gas_services list attr
        """
        xfmrs_config_file = self._network_config["networks"]["elec"]["xfmrs_config"]
        xfmrs_configs = self._read_csv_config(config_file_path=xfmrs_config_file)
        for _, xfmr_config in xfmrs_configs.iterrows():
            connected_services = self._get_children(
                parent_id=xfmr_config["gisid"], all_children=self.elec_services
            )

            connected_secondaries = self._get_children(
                parent_id=xfmr_config["gisid"], all_children=self.elec_secondaries
            )

            connected_assets = connected_services + connected_secondaries

            elec_xfmr = ElecTransformer(
                **xfmr_config, **self._sim_settings, connected_assets=connected_assets
            )

            elec_xfmr.initialize_end_use()
            self.elec_transformers.append(elec_xfmr)

    def _create_elec_primaries(self) -> None:
        """
        Instantiate all necessary ElecPrimaries instances and save to gas_services list attr
        """
        primary_config_file = self._network_config["networks"]["elec"]["primary_config"]
        primary_configs = self._read_csv_config(config_file_path=primary_config_file)
        for _, primary_config in primary_configs.iterrows():
            connected_transformers = self._get_children(
                parent_id=primary_config["gisid"], all_children=self.elec_transformers
            )

            elec_primary = ElecPrimary(
                **primary_config,
                **self._sim_settings,
                connected_assets=connected_transformers
            )

            elec_primary.initialize_end_use()
            self.elec_primaries.append(elec_primary)
