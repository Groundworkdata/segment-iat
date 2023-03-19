"""
Defines a building. A bucket for all end uses
"""
import json
from typing import Dict, List

import numpy as np
import pandas as pd

from end_uses.building_end_uses.clothes_dryer import ClothesDryer
from end_uses.building_end_uses.domestic_hot_water import DHW
from end_uses.building_end_uses.hvac import HVAC
from end_uses.building_end_uses.stove import Stove


ASSET_ENERGY_CONSUMP_KEYS = [
    # stove
    "out.electricity.range_oven.energy_consumption",
    "out.natural_gas.range_oven.energy_consumption",
    "out.propane.range_oven.energy_consumption",
    # clothes dryer
    "out.electricity.clothes_dryer.energy_consumption",
    "out.natural_gas.clothes_dryer.energy_consumption",
    "out.propane.clothes_dryer.energy_consumption",
    # DHW
    "out.electricity.hot_water.energy_consumption",
    "out.natural_gas.hot_water.energy_consumption",
    "out.propane.hot_water.energy_consumption",
    "out.fuel_oil.hot_water.energy_consumption",
    # HVAC
    "out.electricity.heating.energy_consumption",
    "out.electricity.cooling.energy_consumption",
    "out.natural_gas.heating.energy_consumption",
    "out.natural_gas.heating_hp_bkup.energy_consumption", # hybrid configuration
    "out.propane.heating.energy_consumption",
    "out.propane.heating_hp_bkup.energy_consumption", # hybrid configuration
    "out.fuel_oil.heating.energy_consumption",
    "out.fuel_oil.heating_hp_bkup.energy_consumption", #hybrid configuration
]


RESSTOCK_ENERGY_CONSUMP_KEYS = [
    "out.site_energy.total.energy_consumption",
    "out.electricity.total.energy_consumption",
    "out.natural_gas.total.energy_consumption",
    "out.fuel_oil.total.energy_consumption",
    "out.propane.total.energy_consumption",
    # Add assets
    *ASSET_ENERGY_CONSUMP_KEYS
]


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
    def __init__(
            self,
            building_params: dict,
            sim_settings: dict,
            scenario_mapping: List[dict],
    ):
        self.building_params: dict = building_params
        self.sim_settings: dict = sim_settings
        self.scenario_mapping: List[dict] = scenario_mapping
        self.resstock_metadata = building_params.get("resstock_metadata")

        self._year_timestamps: pd.DatetimeIndex = None
        self.years_vec: list = []
        self.building_id: str = ""
        self.end_uses: dict = {}
        self.resstock_scenarios: Dict[int, pd.DataFrame] = {}
        self._main_resstock_retrofit_scenario: int = None
        self.baseline_consumption: pd.DataFrame = None
        self.retrofit_consumption: pd.DataFrame = None

    def populate_building(self) -> None:
        """
        Creates instances of all assets for a given building based on the config file
        """
        # self._get_years_vec()
        self._get_building_id()
        self._get_resstock_buildings()
        self._get_baseline_consumptions()
        self._get_retrofit_consumptions()
        self._create_end_uses()
        self._calc_baseline_energy()
        self._calc_retrofit_energy()

    def _get_years_vec(self) -> None:
        """
        NOT CURRENTLY IN USE
        """
        self.years_vec = list(range(
            self.sim_settings.get("sim_start_year", 2020),
            self.sim_settings.get("sim_end_year", 2050)
        ))

        self._year_timestamps = pd.date_range(
            start="2018-01-01", end="2019-01-01", freq="H", closed="left"
        )

    def _get_building_id(self) -> None:
        self.building_id = self.building_params.get("building_id")

    def _get_resstock_buildings(self) -> None:
        decarb_scenario = self.sim_settings.get("decarb_scenario")
        scenario_params = self.scenario_mapping[decarb_scenario]

        self._main_resstock_retrofit_scenario = scenario_params.get(
            "main_resstock_retrofit_scenario"
        )

        resstock_scenarios = scenario_params.get("resstock_scenarios")
        resstock_scenarios.append(0)
        resstock_scenarios = list(set(resstock_scenarios))

        for i in resstock_scenarios:
            self.resstock_scenarios[i] = self._get_resstock_scenario(i)

    def _get_resstock_scenario(self, i) -> pd.DataFrame:
        return self.resstock_timeseries_connector("MA", i, self.building_params.get("resstock_id"))
    
    def _get_baseline_consumptions(self) -> None:
        self.baseline_consumption = self.resstock_scenarios[0][RESSTOCK_ENERGY_CONSUMP_KEYS]

        for fuel in ["electricity", "natural_gas", "propane", "fuel_oil"]:
            asset_fuel_keys = [i for i in ASSET_ENERGY_CONSUMP_KEYS if fuel in i]
            asset_fuel_consumps = self.baseline_consumption[asset_fuel_keys].sum(axis=1)

            self.baseline_consumption["out.{}.other.energy_consumption".format(fuel)] = (
                self.baseline_consumption["out.{}.total.energy_consumption".format(fuel)]
                - asset_fuel_consumps
            )

    def _get_retrofit_consumptions(self) -> None:
        self.retrofit_consumption = self.resstock_scenarios[
            self._main_resstock_retrofit_scenario
        ][RESSTOCK_ENERGY_CONSUMP_KEYS]

        for fuel in ["electricity", "natural_gas", "propane", "fuel_oil"]:
            asset_fuel_keys = [i for i in ASSET_ENERGY_CONSUMP_KEYS if fuel in i]
            asset_fuel_consumps = self.retrofit_consumption[asset_fuel_keys].sum(axis=1)

            self.retrofit_consumption["out.{}.other.energy_consumption".format(fuel)] = (
                self.retrofit_consumption["out.{}.total.energy_consumption".format(fuel)]
                - asset_fuel_consumps
            )

    def _create_end_uses(self):
        """
        Create the end uses for the building
        """
        end_use_params: List[dict] = self.building_params.get("end_uses", [{}])

        for end_use in end_use_params:
            end_use_type = end_use.get("end_use")
            self.end_uses[end_use_type] = self._get_single_end_use(end_use)

    def _get_single_end_use(self, params: dict):
        config_filepath = params.pop("replacement_config")

        with open(config_filepath) as f:
            data = json.load(f)

        end_use_params = data

        if params.get("end_use") == "stove":
            stove = Stove(
                params.pop("original_energy_source"),
                self.resstock_scenarios,
                self.scenario_mapping,
                self.sim_settings.get("decarb_scenario"),
                self.resstock_metadata,
                **end_use_params,
            )

            stove.initialize_end_use()

            return stove
        
        if params.get("end_use") == "clothes_dryer":
            dryer = ClothesDryer(
                params.pop("original_energy_source"),
                self.resstock_scenarios,
                self.scenario_mapping,
                self.sim_settings.get("decarb_scenario"),
                self.resstock_metadata,
                **end_use_params,
            )

            dryer.initialize_end_use()

            return dryer
        
        if params.get("end_use") == "domestic_hot_water":
            dhw = DHW(
                params.pop("original_energy_source"),
                self.resstock_scenarios,
                self.scenario_mapping,
                self.sim_settings.get("decarb_scenario"),
                **end_use_params
            )

            dhw.initialize_end_use()

            return dhw
        
        if params.get("end_use") == "hvac":
            hvac = HVAC(
                params.pop("original_energy_source"),
                self.resstock_scenarios,
                self.scenario_mapping,
                self.sim_settings.get("decarb_scenario"),
                self.resstock_metadata,
                **end_use_params
            )

            hvac.initialize_end_use()

            return hvac

        return None
    
    def _calc_baseline_energy(self) -> None:
        """
        Steps:
        1. Get a single asset
        2. Get all asset energies and add them to the building consumption dataframe with underscore
            "update"
        3. Repeat 1 and 2 for all assets
        4. Get all asset consumptions ("_update") of a given energy type
        5. Get the building "other" consumption for that energy type
        6. Calculate the updated total building consumption for that energy type as the sum of 4 & 5
        7. Repeat 4-6 for all energy types
        """
        for asset_type in ["stove", "clothes_dryer", "domestic_hot_water", "hvac"]:
            if asset_type in self.end_uses:
                asset = self.end_uses.get(asset_type)

                baseline_energies_asset = asset.baseline_energy_use

                self.baseline_consumption = pd.concat(
                    [
                        self.baseline_consumption,
                        baseline_energies_asset.rename(
                            columns={
                                col: "{}_update".format(col) for col in baseline_energies_asset
                            }
                        )
                    ],
                    axis=1
                )

        asset_updates = [i for i in self.baseline_consumption.columns if i.endswith("_update")]

        for fuel in ["electricity", "natural_gas", "propane", "fuel_oil"]:
            asset_update_consump_keys = [
                i for i in asset_updates if i.startswith("out.{}".format(fuel))
            ]
            asset_update_consump_keys.append("out.{}.other.energy_consumption".format(fuel))

            self.baseline_consumption["out.{}.total.energy_consumption_update".format(fuel)] = \
                self.baseline_consumption[asset_update_consump_keys].sum(axis=1)

    def _calc_retrofit_energy(self) -> None:
        """
        Steps are same as _calc_baseline_energy
        """
        for asset_type in ["stove", "clothes_dryer", "domestic_hot_water", "hvac"]:
            if asset_type in self.end_uses:
                asset = self.end_uses.get(asset_type)

                retrofit_energies_stove = asset.retrofit_energy_use

                self.retrofit_consumption = pd.concat(
                    [
                        self.retrofit_consumption,
                        retrofit_energies_stove.rename(
                            columns={
                                col: "{}_update".format(col) for col in retrofit_energies_stove
                            }
                        )
                    ],
                    axis=1
                )

        asset_updates = [i for i in self.retrofit_consumption.columns if i.endswith("_update")]

        for fuel in ["electricity", "natural_gas", "propane", "fuel_oil"]:
            asset_update_consump_keys = [
                i for i in asset_updates if i.startswith("out.{}".format(fuel))
            ]
            asset_update_consump_keys.append("out.{}.other.energy_consumption".format(fuel))

            self.retrofit_consumption["out.{}.total.energy_consumption_update".format(fuel)] = \
                self.retrofit_consumption[asset_update_consump_keys].sum(axis=1)

    def write_building_energy_info(self) -> None:
        """
        Write calcualted building information for energy use
        """
        self.baseline_consumption.to_csv(
            "./outputs/{}_baseline_consump.csv".format(self.building_id)
        )

        self.retrofit_consumption.to_csv(
            "./outputs/{}_retrofit_consump.csv".format(self.building_id)
        )

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

    @staticmethod
    def resstock_timeseries_connector(state: str, scenario: int, building_id: int) -> pd.DataFrame:
        """
        ResStock connection for the 2022 release 1.1 for timeseries data

        Args:
            state (str): The state code
            scenario (int): The simulation scenario
            building_id (int): The ID of the individual building
        """
        BUILDING_BASE_URL = "https://oedi-data-lake.s3.amazonaws.com/"\
                    "nrel-pds-building-stock/end-use-load-profiles-for-us-building-stock/2022/"\
                    "resstock_amy2018_release_1.1/timeseries_individual_buildings/by_state/"

        building_url = BUILDING_BASE_URL + "upgrade={0}/state={1}/{2}-{0}.parquet".format(
            scenario, state, building_id
        )

        response = pd.read_parquet(building_url)

        return response
    
    #TODO: Read in metadata so we can get the ResStock input data for scenarios
