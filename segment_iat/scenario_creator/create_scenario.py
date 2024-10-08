"""
Creates and run a scenario based on provided configuration files
"""
import os
from typing import Dict, List

import numpy as np
import pandas as pd

from segment_iat.buildings.building import Building
from segment_iat.utility_network.utility_network import UtilityNetwork
from segment_iat.utils.incentives import Incentives


DEFAULT_SIM_START_YEAR = 2020
DEFAULT_SIM_END_YEAR = 2050
DEFAULT_ASSET_LIFETIME = 30
DEFAULT_REPLACEMENT_COST_DOLLARS_YEAR = 2022

FUELS = ["electricity", "natural_gas", "propane", "fuel_oil", "thermal_cooling", "thermal_heating"]

OUTPUTS_BASEPATH = "./outputs"

DOMAIN_BUILDING = "building"
TYPE_BUILDING_AGGREGATE = "building_aggregate"
TYPE_BUILDING_GROSS = "building_gross"
TYPE_BUILDING_NET = "building_net"
TYPE_BUILDING_INCENTIVE = "building_incentive"

DOMAIN_ELEC = "elec_network"
TYPE_ELEC_XMFR = "elec_xmfr"

DOMAIN_GAS = "gas_network"
TYPE_GAS_MAIN = "gas_main"
TYPE_GAS_SERVICE = "gas_service"
TYPE_GAS_METER = "gas_meter"

DOMAIN_THERMAL = "thermal_network"
TYPE_THERMAL = "thermal_network"


class ScenarioCreator:
    """
    Executes a scenario simulation for a given street segment and writes outputs to CSVs

    Args:
        sim_settings_filepath (str): The filepath for the simulation settings configuration JSON

    Optional args:
        write_building_energy_timeseries (bool): If True, write the hourly energy consumption for
            each building to a CSV

    Attributes:
        street_segment (str): The ID of the street segment being simulated
        buildings (Dict[str, Building]): Dict of instantiated Building objects, mapped by parcel ID
        utility_network (UtilityNetwork): Instantiated UtilityNetwork object for the street segment

    Methods:
        create_scenario (None): Executes the simulation
    """

    def __init__(
            self,
            segment_name: str,
            study_zip: int,
            study_start_year: int,
            study_end_year: int,
            gas_pipe_intervention_year: int,
            parcels_table: dict,
            sim_settings_filepath: str,
            write_building_energy_timeseries: bool = False,
            status_logging=None
    ):
        self.segment_name: str = segment_name
        self.study_zip: int = study_zip
        self.study_start_year: int = study_start_year
        self.study_end_year: int = study_end_year
        self.gas_pipe_intervention_year: int = gas_pipe_intervention_year
        self.parcel_table: dict = parcels_table
        self._sim_settings_filepath: str = sim_settings_filepath
        self.write_building_energy_timeseries: bool = write_building_energy_timeseries
        self.status_logging = status_logging

        self._sim_config: dict = {}
        self._outputs_path: str = ""
        self._years_vec: List[int] = []
        self._buildings_config: dict = {}
        self.parcel_scenario_table: dict = {}

        self.sim_name: str = ""
        self.street_segment: str = ""
        self.incentives: Incentives = None
        self.buildings: Dict[str, Building] = {}
        self.utility_network: UtilityNetwork = None

    def create_scenario(self):
        self._sim_config = self._get_sim_settings()
        self.street_segment = self._get_street_segment()
        self.sim_name = self._get_sim_name()
        self._outputs_path = self._set_outputs_path()
        self._years_vec = self._get_years_vec()
        self._status_update("Creating buildings...", 0.25)
        self.parcel_scenario_table = self._get_parcel_scenario_table()
        self.incentives = self._gather_incentives()
        self._create_building()
        self._status_update("Creating utility network...", 0.8)
        self._create_utility_network()
        self._write_outputs()
        self._get_utility_network_outputs()
        self._status_update("Simulation complete!", 1.0)

    def _get_sim_settings(self) -> dict:
        """
        Read in simulation settings
        """
        settings = pd.read_csv(self._sim_settings_filepath, index_col=0, header=None)
        settings = settings.iloc[:, 0].to_dict()
        settings["sim_start_year"] = self.study_start_year
        settings["sim_end_year"] = self.study_end_year
        settings["zip_code"] = self.study_zip
        settings["gas_pipe_intervention_year"] = self.gas_pipe_intervention_year
        settings["segment_id"] = self.segment_name
        return settings

    def _get_street_segment(self) -> str:
        """
        Return the street segment ID
        """
        return self.segment_name
    
    def _get_sim_name(self) -> str:
        """
        Return the simulation name
        """
        return self._sim_config.get("scenario_name")

    def _set_outputs_path(self) -> str:
        """
        Set the outputs filepath for this simulation
        """
        outputs_filepath = os.path.join(
            OUTPUTS_BASEPATH,
            self.street_segment,
            self.sim_name
        )

        if not os.path.exists(outputs_filepath):
            os.makedirs(outputs_filepath)

        return outputs_filepath

    def _get_years_vec(self) -> List[int]:
        return list(range(
            self._sim_config.get("sim_start_year", DEFAULT_SIM_START_YEAR),
            self._sim_config.get("sim_end_year", DEFAULT_SIM_END_YEAR)
        ))

    def _get_parcel_scenario_table(self) -> dict:
        """
        Get table of parcel data pertinent to the given simulation
        """
        measures_id = self._sim_config.get("parcel_retrofit_measures_filename")
        filepath = f"./config_files/{self.street_segment}/parcels/{measures_id}.csv"
        parcel_scenario_table = pd.read_csv(filepath).set_index("parcel_id")
        return parcel_scenario_table.to_dict(orient="index")
    
    def _gather_incentives(self) -> Incentives:
        """
        Instantiate an instance of the Incentives class and populate the object
        """
        incentives = Incentives(self.study_zip)
        incentives.gather_incentives()
        return incentives

    def _create_building(self) -> None:
        parcels = self.parcel_table.keys()
        num_buildings = len(parcels)
        building_num = 0

        for building_id in parcels:
            building_num += 1
            self._status_update(
                f"Creating building {building_num} of {num_buildings}",
                (building_num / num_buildings) * 0.5 + 0.25
            )

            building_params = self.parcel_table.get(building_id)
            building_scenario_params = self.parcel_scenario_table.get(building_id)

            building_params = {
                "building_id": building_id,
                "baseline_consumption_id": building_params.get("baseline_consumption_id"),
                "retrofit_consumption_id": building_scenario_params.get("energy_profile_id"),
                "load_scaling_factor": building_params.get("load_scaling_factor"),
                "asset_install_year": building_params.get("install_year"),
                "asset_replacement_year": building_scenario_params.get("install_year"),
                "heating_fuel": building_params.get("heating_fuel"),
                "retrofit_heating_fuel": building_scenario_params.get("heating_fuel"),
                "existing_measures_cost_id": building_params.get("measure_costs_filename"),
                "retrofit_measures_cost_id": self._sim_config.get("parcel_retrofit_measure_costs_filename"),
                "hvac.end_use_retrofit_item": building_scenario_params.get("hvac"),
                "domestic_hot_water.end_use_retrofit_item": building_scenario_params.get("domestic_hot_water"),
                "clothes_dryer.end_use_retrofit_item": building_scenario_params.get("clothes_dryer"),
                "stove.end_use_retrofit_item": building_scenario_params.get("stove"),
            }

            building = Building(
                building_params,
                self._sim_config,
                self.incentives.incentives
            )

            building.populate_building()

            if self.write_building_energy_timeseries:
                building.write_building_energy_info()

            self.buildings[building.building_id] = building

    def _create_utility_network(self):
        """
        Create the utility network based on the input config
        """
        segment_id = self._sim_config["segment_id"]
        utility_network_config_filepath = f"./config_files/{segment_id}/utility_network/"

        self.utility_network = UtilityNetwork(
            utility_network_config_filepath, self._sim_config, self.buildings
        )

        self.utility_network.populate_utility_network()

    def _write_outputs(self) -> None:
        """
        Write output tables from all buildings
        """
        self._status_update("Writing outputs", 0.9)

        years_vec = pd.Index(data=self._years_vec, name="year")

        # ---Is Retrofit Vec---
        all_dfs = []
        for building_id, building in self.buildings.items():
            df = pd.DataFrame({"year": years_vec, "is_retrofit": building._is_retrofit_vec})
            df.loc[:, "asset_id"] = building_id
            df.loc[:, "asset_domain"] = DOMAIN_BUILDING
            df.loc[:, "asset_type"] = TYPE_BUILDING_AGGREGATE
            all_dfs.append(df)

        for xmfr in self.utility_network.elec_transformers:
            df = pd.DataFrame({
                "year": years_vec,
                "is_retrofit": xmfr.is_replacement_vector
            })
            df.loc[:, "asset_id"] = xmfr.asset_id
            df.loc[:, "asset_domain"] = DOMAIN_ELEC
            df.loc[:, "asset_type"] = TYPE_ELEC_XMFR
            all_dfs.append(df)

        for gas_service in self.utility_network.gas_services:
            df = pd.DataFrame({
                "year": years_vec,
                "is_retrofit": gas_service.retrofit_vector
            })
            df.loc[:, "asset_id"] = gas_service.asset_id
            df.loc[:, "asset_domain"] = DOMAIN_GAS
            df.loc[:, "asset_type"] = TYPE_GAS_SERVICE
            all_dfs.append(df)

        for gas_main in self.utility_network.gas_mains:
            df = pd.DataFrame({
                "year": years_vec,
                "is_retrofit": gas_main.retrofit_vector
            })
            df.loc[:, "asset_id"] = gas_main.asset_id
            df.loc[:, "asset_domain"] = DOMAIN_GAS
            df.loc[:, "asset_type"] = TYPE_GAS_MAIN
            all_dfs.append(df)

        all_dfs = pd.concat(all_dfs)
        all_dfs.to_csv(os.path.join(self._outputs_path, "is_retrofit_vec_table.csv"), index=False)

        # ---Retrofit year---
        all_dfs = []
        for building_id, building in self.buildings.items():
            df = pd.DataFrame({"year": years_vec, "retrofit_year": building._retrofit_vec})
            df.loc[:, "asset_id"] = building_id
            df.loc[:, "asset_domain"] = DOMAIN_BUILDING
            df.loc[:, "asset_type"] = TYPE_BUILDING_AGGREGATE
            all_dfs.append(df)

        for xmfr in self.utility_network.elec_transformers:
            df = pd.DataFrame({
                "year": years_vec,
                "retrofit_year": xmfr.retrofit_vector
            })
            df.loc[:, "asset_id"] = xmfr.asset_id
            df.loc[:, "asset_domain"] = DOMAIN_ELEC
            df.loc[:, "asset_type"] = TYPE_ELEC_XMFR
            all_dfs.append(df)

        for gas_service in self.utility_network.gas_services:
            df = pd.DataFrame({
                "year": years_vec,
                "retrofit_year": gas_service.replacement_vector
            })
            df.loc[:, "asset_id"] = gas_service.asset_id
            df.loc[:, "asset_domain"] = DOMAIN_GAS
            df.loc[:, "asset_type"] = TYPE_GAS_SERVICE
            all_dfs.append(df)

        for gas_main in self.utility_network.gas_mains:
            df = pd.DataFrame({
                "year": years_vec,
                "retrofit_year": gas_main.replacement_vector
            })
            df.loc[:, "asset_id"] = gas_main.asset_id
            df.loc[:, "asset_domain"] = DOMAIN_GAS
            df.loc[:, "asset_type"] = TYPE_GAS_MAIN
            all_dfs.append(df)

        all_dfs = pd.concat(all_dfs)
        all_dfs.to_csv(os.path.join(self._outputs_path, "retrofit_year.csv"), index=False)

        # ---Retrofit cost---
        all_dfs = []
        for building_id, building in self.buildings.items():
            df = pd.DataFrame({
                "year": years_vec,
                "retrofit_cost": building.retrofit_cost_gross
            })
            df.loc[:, "asset_id"] = building_id
            df.loc[:, "asset_domain"] = DOMAIN_BUILDING
            df.loc[:, "asset_type"] = TYPE_BUILDING_GROSS
            all_dfs.append(df)

            df = pd.DataFrame({
                "year": years_vec,
                "retrofit_cost": building.retrofit_incentive_vec
            })
            df.loc[:, "asset_id"] = building_id
            df.loc[:, "asset_domain"] = DOMAIN_BUILDING
            df.loc[:, "asset_type"] = TYPE_BUILDING_INCENTIVE
            all_dfs.append(df)

            df = pd.DataFrame({
                "year": years_vec,
                "retrofit_cost": building.retrofit_cost_net
            })
            df.loc[:, "asset_id"] = building_id
            df.loc[:, "asset_domain"] = DOMAIN_BUILDING
            df.loc[:, "asset_type"] = TYPE_BUILDING_NET
            all_dfs.append(df)

        for xmfr in self.utility_network.elec_transformers:
            df = pd.DataFrame({
                "year": years_vec,
                "retrofit_cost": xmfr.upgrade_cost
            })
            df.loc[:, "asset_id"] = xmfr.asset_id
            df.loc[:, "asset_domain"] = DOMAIN_ELEC
            df.loc[:, "asset_type"] = TYPE_ELEC_XMFR
            all_dfs.append(df)

        for gas_meter in self.utility_network.gas_meters:
            df = pd.DataFrame({
                "year": years_vec,
                "retrofit_cost": gas_meter.get_retrofit_cost()
            })
            df.loc[:, "asset_id"] = gas_meter.asset_id
            df.loc[:, "asset_domain"] = DOMAIN_GAS
            df.loc[:, "asset_type"] = TYPE_GAS_METER
            all_dfs.append(df)

        for gas_service in self.utility_network.gas_services:
            df = pd.DataFrame({
                "year": years_vec,
                "retrofit_cost": gas_service.get_install_cost()
            })
            df.loc[:, "asset_id"] = gas_service.asset_id
            df.loc[:, "asset_domain"] = DOMAIN_GAS
            df.loc[:, "asset_type"] = TYPE_GAS_SERVICE
            all_dfs.append(df)

        for gas_main in self.utility_network.gas_mains:
            total_cost = (
                np.array(gas_main.get_install_cost())
                + np.array(gas_main.get_system_shutoff_cost())
            ).tolist()

            df = pd.DataFrame({
                "year": years_vec,
                "retrofit_cost": total_cost
            })
            df.loc[:, "asset_id"] = gas_main.asset_id
            df.loc[:, "asset_domain"] = DOMAIN_GAS
            df.loc[:, "asset_type"] = TYPE_GAS_MAIN
            all_dfs.append(df)

        if self.utility_network.thermal_energy_network:
            ten = self.utility_network.thermal_energy_network
            df = pd.DataFrame({
                "year": years_vec,
                "retrofit_cost": ten.install_cost_vec
            })
            df.loc[:, "asset_id"] = ten.asset_id
            df.loc[:, "asset_domain"] = DOMAIN_THERMAL
            df.loc[:, "asset_type"] = TYPE_THERMAL
            all_dfs.append(df)

        all_dfs = pd.concat(all_dfs)
        all_dfs.to_csv(os.path.join(self._outputs_path, "retrofit_cost.csv"), index=False)

        # ---Book value---
        all_dfs = []
        for building_id, building in self.buildings.items():
            # ---Replacement asset book value---
            df = pd.DataFrame({
                "year": years_vec,
                "book_val": building._get_retrofit_book_value_vec()
            })
            df.loc[:, "asset_id"] = building_id
            df.loc[:, "existing_or_retrofit"] = "retrofit"
            df.loc[:, "asset_domain"] = DOMAIN_BUILDING
            df.loc[:, "asset_type"] = TYPE_BUILDING_AGGREGATE
            all_dfs.append(df)

            # ---Existing book val---
            df = pd.DataFrame({
                "year": years_vec,
                "book_val": building._get_exising_book_val_vec()
            })
            df.loc[:, "asset_id"] = building_id
            df.loc[:, "existing_or_retrofit"] = "existing"
            df.loc[:, "asset_domain"] = DOMAIN_BUILDING
            df.loc[:, "asset_type"] = TYPE_BUILDING_AGGREGATE
            all_dfs.append(df)

        for gas_service in self.utility_network.gas_services:
            df = pd.DataFrame({
                "year": years_vec,
                "book_val": gas_service.book_value
            })
            df.loc[:, "asset_id"] = gas_service.asset_id
            df.loc[:, "existing_or_retrofit"] = "retrofit"
            df.loc[:, "asset_domain"] = DOMAIN_GAS
            df.loc[:, "asset_type"] = TYPE_GAS_SERVICE
            all_dfs.append(df)

        for gas_main in self.utility_network.gas_mains:
            df = pd.DataFrame({
                "year": years_vec,
                "book_val": gas_main.book_value
            })
            df.loc[:, "asset_id"] = gas_main.asset_id
            df.loc[:, "existing_or_retrofit"] = "retrofit"
            df.loc[:, "asset_domain"] = DOMAIN_GAS
            df.loc[:, "asset_type"] = TYPE_GAS_MAIN
            all_dfs.append(df)

        if self.utility_network.thermal_energy_network:
            ten = self.utility_network.thermal_energy_network
            df = pd.DataFrame({
                "year": years_vec,
                "book_val": ten.book_value_vec
            })
            df.loc[:, "asset_id"] = ten.asset_id
            # This flag doesn't really apply to TENs, but including for consistency
            df.loc[:, "existing_or_retrofit"] = "retrofit"
            df.loc[:, "asset_domain"] = DOMAIN_THERMAL
            df.loc[:, "asset_type"] = TYPE_THERMAL
            all_dfs.append(df)

        all_dfs = pd.concat(all_dfs)
        all_dfs.to_csv(os.path.join(self._outputs_path, "book_val.csv"), index=False)

        # ---Stranded val---
        all_dfs = []
        for building_id, building in self.buildings.items():
            df = pd.DataFrame({
                "year": years_vec,
                "stranded_val": building._get_exising_stranded_val_vec()
            })
            df.loc[:, "asset_id"] = building_id
            df.loc[:, "asset_domain"] = DOMAIN_BUILDING
            df.loc[:, "asset_type"] = TYPE_BUILDING_AGGREGATE
            df.loc[:, "existing_or_retrofit"] = "existing"
            all_dfs.append(df)

        for gas_service in self.utility_network.gas_services:
            df = pd.DataFrame({
                "year": years_vec,
                "stranded_val": gas_service.stranded_value
            })
            df.loc[:, "asset_id"] = gas_service.asset_id
            df.loc[:, "asset_domain"] = DOMAIN_GAS
            df.loc[:, "asset_type"] = TYPE_GAS_SERVICE
            df.loc[:, "existing_or_retrofit"] = "retrofit"
            all_dfs.append(df)

        for gas_main in self.utility_network.gas_mains:
            df = pd.DataFrame({
                "year": years_vec,
                "stranded_val": gas_main.stranded_value
            })
            df.loc[:, "asset_id"] = gas_main.asset_id
            df.loc[:, "asset_domain"] = DOMAIN_GAS
            df.loc[:, "asset_type"] = TYPE_GAS_MAIN
            df.loc[:, "existing_or_retrofit"] = "retrofit"
            all_dfs.append(df)

        all_dfs = pd.concat(all_dfs)
        all_dfs.to_csv(os.path.join(self._outputs_path, "stranded_val.csv"), index=False)

        # ---Incentive data---
        all_dfs = []
        for bldg_id, bldg in self.buildings.items():
            df = pd.DataFrame(bldg.calculated_incentives)
            df.loc[:, "asset_id"] = bldg_id
            all_dfs.append(df)

        all_dfs = pd.concat(all_dfs)
        all_dfs.to_csv(os.path.join(self._outputs_path, "incentives.csv"), index=False)

        # ---Energy use---
        building_energy_usage = {
            building_id: building.annual_energy_by_fuel
            for building_id, building in self.buildings.items()
        }

        all_dfs = []
        for building_id, building_consumptions in building_energy_usage.items():
            for fuel in FUELS:
                df = pd.DataFrame({"year": years_vec, "consumption": building_consumptions[fuel]})
                df.loc[:, "asset_id"] = building_id
                df.loc[:, "energy_type"] = fuel
                df.loc[:, "asset_domain"] = DOMAIN_BUILDING
                df.loc[:, "asset_type"] = TYPE_BUILDING_AGGREGATE
                all_dfs.append(df)

        xmfr_energy_usage = {
            xmfr.asset_id: list(xmfr.annual_total_energy_use.values())
            for xmfr in self.utility_network.elec_transformers
        }

        for asset_id, elec_consumption in xmfr_energy_usage.items():
            df = pd.DataFrame({"year": years_vec, "consumption": elec_consumption})
            df.loc[:, "asset_id"] = asset_id
            df.loc[:, "energy_type"] = "electricity"
            df.loc[:, "asset_domain"] = DOMAIN_ELEC
            df.loc[:, "asset_type"] = TYPE_ELEC_XMFR
            all_dfs.append(df)

        thermal_network = self.utility_network.thermal_energy_network
        if thermal_network:
            df = pd.DataFrame({"year": years_vec, "consumption": thermal_network.annual_load_cooling})
            df.loc[:, "asset_id"] = thermal_network.asset_id
            df.loc[:, "energy_type"] = "thermal_cooling"
            df.loc[:, "asset_domain"] = DOMAIN_THERMAL
            df.loc[:, "asset_type"] = TYPE_THERMAL
            all_dfs.append(df)

            df = pd.DataFrame({"year": years_vec, "consumption": thermal_network.annual_load_heating})
            df.loc[:, "asset_id"] = thermal_network.asset_id
            df.loc[:, "energy_type"] = "thermal_heating"
            df.loc[:, "asset_domain"] = DOMAIN_THERMAL
            df.loc[:, "asset_type"] = TYPE_THERMAL
            all_dfs.append(df)

        all_dfs = pd.concat(all_dfs)
        all_dfs.to_csv(os.path.join(self._outputs_path, "energy_consumption.csv"), index=False)

        # ---Peak energy use---
        all_dfs = []
        xmfr_peak = {
            xmfr.asset_id: xmfr.annual_peak_energy_use
            for xmfr in self.utility_network.elec_transformers
        }

        for asset_id, peak_consump in xmfr_peak.items():
            df = pd.DataFrame({"year": years_vec, "peak_consump": peak_consump})
            df.loc[:, "asset_id"] = asset_id
            df.loc[:, "energy_type"] = "electricity"
            df.loc[:, "asset_domain"] = DOMAIN_ELEC
            df.loc[:, "asset_type"] = TYPE_ELEC_XMFR
            all_dfs.append(df)

        thermal_network = self.utility_network.thermal_energy_network
        if thermal_network:
            df = pd.DataFrame({"year": years_vec, "peak_consump": thermal_network.annual_peak_cooling})
            df.loc[:, "asset_id"] = thermal_network.asset_id
            df.loc[:, "energy_type"] = "thermal_cooling"
            df.loc[:, "asset_domain"] = DOMAIN_THERMAL
            df.loc[:, "asset_type"] = TYPE_THERMAL
            all_dfs.append(df)

            df = pd.DataFrame({"year": years_vec, "peak_consump": thermal_network.annual_peak_heating})
            df.loc[:, "asset_id"] = thermal_network.asset_id
            df.loc[:, "energy_type"] = "thermal_heating"
            df.loc[:, "asset_domain"] = DOMAIN_THERMAL
            df.loc[:, "asset_type"] = TYPE_THERMAL
            all_dfs.append(df)

        all_dfs = pd.concat(all_dfs)
        all_dfs.to_csv(os.path.join(self._outputs_path, "peak_consump.csv"), index=False)

        # ---Building utility costs---
        building_util_costs = {
            building_id: building._calc_building_utility_costs()
            for building_id, building in self.buildings.items()
        }

        all_dfs = []
        for building_id, costs in building_util_costs.items():
            for fuel in FUELS:
                df = pd.DataFrame({
                    "year": years_vec,
                    "consumption_costs": costs[fuel]
                })
                df.loc[:, "asset_id"] = building_id
                df.loc[:, "energy_type"] = fuel
                df.loc[:, "asset_domain"] = DOMAIN_BUILDING
                df.loc[:, "asset_type"] = TYPE_BUILDING_AGGREGATE
                all_dfs.append(df)
        all_dfs = pd.concat(all_dfs)
        all_dfs.to_csv(os.path.join(self._outputs_path, "consumption_costs.csv"), index=False)

        # ---Building fuel---
        all_dfs = []
        for building_id, building in self.buildings.items():
            df = pd.DataFrame({"year": years_vec, "fuel_type": building._fuel_type})
            df.loc[:, "asset_id"] = building_id
            df.loc[:, "asset_domain"] = DOMAIN_BUILDING
            df.loc[:, "asset_type"] = TYPE_BUILDING_AGGREGATE
            all_dfs.append(df)
        all_dfs = pd.concat(all_dfs)
        all_dfs.to_csv(os.path.join(self._outputs_path, "fuel_type.csv"), index=False)

        # ---Methane leaks---
        all_dfs = []
        # Building leaks
        for building_id, building in self.buildings.items():
            df = pd.DataFrame({"year": years_vec, "leaks": building._methane_leaks})
            df.loc[:, "asset_id"] = building_id
            df.loc[:, "asset_domain"] = DOMAIN_BUILDING
            df.loc[:, "asset_type"] = TYPE_BUILDING_AGGREGATE
            all_dfs.append(df)

        # Gas service leaks
        for service in self.utility_network.gas_services:
            df = pd.DataFrame({
                "year": years_vec,
                "leaks": service.annual_total_leakage
            })
            df.loc[:, "asset_id"] = service.asset_id
            df.loc[:, "asset_domain"] = DOMAIN_GAS
            df.loc[:, "asset_type"] = TYPE_GAS_SERVICE
            all_dfs.append(df)

        # Gas main leaks
        for main in self.utility_network.gas_mains:
            df = pd.DataFrame({
                "year": years_vec,
                "leaks": main.annual_total_leakage
            })
            df.loc[:, "asset_id"] = main.asset_id
            df.loc[:, "asset_domain"] = DOMAIN_GAS
            df.loc[:, "asset_type"] = TYPE_GAS_MAIN
            all_dfs.append(df)
        all_dfs = pd.concat(all_dfs)
        all_dfs.to_csv(os.path.join(self._outputs_path, "methane_leaks.csv"), index=False)

        # ---Combustion emissions---
        all_dfs = []
        for building_id, building in self.buildings.items():
            for fuel in FUELS:
                df = pd.DataFrame({
                    "year": years_vec,
                    "consumption_emissions": building._combustion_emissions[fuel]
                })
                df.loc[:, "asset_id"] = building_id
                df.loc[:, "energy_type"] = fuel
                df.loc[:, "asset_domain"] = DOMAIN_BUILDING
                df.loc[:, "asset_type"] = TYPE_BUILDING_AGGREGATE
                all_dfs.append(df)
        all_dfs = pd.concat(all_dfs)
        all_dfs.to_csv(os.path.join(self._outputs_path, "consumption_emissions.csv"), index=False)


        # ---O&M costs---
        all_dfs = []
        for gas_service in self.utility_network.gas_services:
            df = pd.DataFrame({
                "year": years_vec,
                "annual_operating_costs": gas_service.annual_operating_expenses
            })
            df.loc[:, "asset_id"] = gas_service.asset_id
            df.loc[:, "asset_domain"] = DOMAIN_GAS
            df.loc[:, "asset_type"] = TYPE_GAS_SERVICE
            all_dfs.append(df)

        for gas_main in self.utility_network.gas_mains:
            df = pd.DataFrame({
                "year": years_vec,
                "annual_operating_costs": gas_main.annual_operating_expenses
            })
            df.loc[:, "asset_id"] = gas_main.asset_id
            df.loc[:, "asset_domain"] = DOMAIN_GAS
            df.loc[:, "asset_type"] = TYPE_GAS_MAIN
            all_dfs.append(df)

        if self.utility_network.thermal_energy_network:
            ten = self.utility_network.thermal_energy_network
            df = pd.DataFrame({
                "year": years_vec,
                "annual_operating_costs": ten.annual_om_vec
            })
            df.loc[:, "asset_id"] = ten.asset_id
            df.loc[:, "asset_domain"] = DOMAIN_THERMAL
            df.loc[:, "asset_type"] = TYPE_THERMAL
            all_dfs.append(df)

        all_dfs = pd.concat(all_dfs)
        all_dfs.to_csv(os.path.join(self._outputs_path, "operating_costs.csv"), index=False)

    def _get_utility_network_outputs(self):
        """
        Printing out some utility network stuff. Will need to write to output tables soon...
        """
        print("=====Meters=====")
        meters = []
        for meter in self.utility_network.elec_meters:
            meters.append(
                {
                    "meter_id": meter.asset_id,
                    "building_id": meter.building.building_id,
                    "parent_id": meter.parent_id,
                }
            )
        print(pd.DataFrame(meters))

        print("=====XMFR=====")
        xmfrs = []
        for xmfr in self.utility_network.elec_transformers:
            xmfrs.append(
                {
                    "connected_assets": [asset.asset_id for asset in xmfr.connected_assets],
                    "xmfr_id": xmfr.asset_id,
                    "parent_id": xmfr.parent_id,
                }
            )
        print(pd.DataFrame(xmfrs))

    def _status_update(self, msg: str, pct: float) -> None:
        """
        Display a status message on the progress of the simulation
        """
        if self.status_logging:
            self.status_logging.progress(pct, msg)
        else:
            print(msg)
