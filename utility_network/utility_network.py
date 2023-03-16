"""
Defines a utility network. A bucket for all utility assets
"""
from typing import List, Dict
import pandas as pd

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
    
        self._year_timestamps: pd.DatetimeIndex = None
        self.years_vec: list = []

        self.gas_main: List[GasMain] = []
        self.gas_services: List[GasService] = []
        self.gas_meters: List[GasMeter] = []
        self.elec_meters: List[ElecMeter] = []

    def populate_utility_network(self) -> None:
        """
        Calls all functions to populate the utility network
        """
        self._read_config()
        self._get_years_vec()
        self._create_gas_mains()
        self._create_gas_services()
        self._get_gas_meters()
        self._get_elec_meters()

    def _read_config(self) -> None:
        """
        Read in the utilty network config file and save to network_config attr
        """
        with open(self._network_config_filepath) as f:
            data = json.load(f)

        self.network_config = data

    def _get_years_vec(self) -> None:
        self.years_vec = list(range(
            self.sim_settings.get("sim_start_year", 2020),
            self.sim_settings.get("sim_end_year", 2050)
        ))

        self._year_timestamps = pd.date_range(
            start="2018-01-01", end="2019-01-01", freq="H", closed="left"
        )

    def _create_gas_mains(self) -> None:
        """
        Instantiate the GasMain and write to gas_main attr
        """
        main_config = self.network_config.get("gas_main")
        self.gas_main = GasMain(**main_config, **self.sim_settings)

    def _create_gas_services(self) -> None:
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

    def write_network_cost_info(self) -> None:
        """
        Write calculated network information for total costs
        """

        asset_type = "main"
        costs_df = self._sum_end_use_figures("install_cost", asset_type=asset_type)
        depreciations_df = self._sum_end_use_figures("depreciation", asset_type=asset_type)
        stranded_value_df = self._sum_end_use_figures("stranded_value", asset_type=asset_type)

        full_costs_df = pd.merge(costs_df, depreciations_df, left_index=True, right_index=True)
        full_costs_df = pd.merge(
            full_costs_df, stranded_value_df, left_index=True, right_index=True
        )

        full_costs_df.to_csv("./{}_costs.csv".format(asset_type), index_label="year")


    def write_network_energy_info(self) -> None:
        """
        Write calculated network information for total costs
        """
        asset_type = "main"
        consump_df = self._sum_end_use_figures("gas_consump_annual", asset_type=asset_type)
        peak_df = self._sum_end_use_figures("gas_peak_annual", asset_type=asset_type)
        leakage_df = self._sum_end_use_figures("gas_leakage_annual", asset_type=asset_type)

        full_info_df = pd.merge(consump_df, peak_df, left_index=True, right_index=True)
        full_info_df = pd.merge(
            full_info_df, leakage_df, left_index=True, right_index=True
        )

        full_info_df.to_csv("./{}_usage_info.csv".format(asset_type), index_label="year")


    def _sum_end_use_figures(self, cost_figure, asset_type) -> pd.DataFrame:
        """
        cost_figure must be in [
            "install_cost", "depreciation", "stranded_value",
            "elec_consump_annual", "gas_consump_annual", "elec_peak_annual", "gas_peak_annual", "gas_leakage_annual"
        ]
        """
        costs = {}

        if asset_type == "main":
            for asset_id, asset_ in self.gas_main.items():
                costs[asset_id + "_{}".format(cost_figure)] = getattr(asset_, cost_figure)

        if asset_type == "service":
            for asset_id, asset_ in self.gas_services.items():
                costs[asset_id + "_{}".format(cost_figure)] = getattr(asset_, cost_figure)

        costs_df = pd.DataFrame(costs)
        costs_df.index = self.years_vec

        costs_df["total_{}".format(cost_figure)] = costs_df.sum(axis=1)

        return costs_df
