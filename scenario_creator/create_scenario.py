"""
Creates a scenario based on input values
"""
import json
import os
from typing import Dict, List

import pandas as pd

from buildings.building import Building
from utility_network.utility_network import UtilityNetwork


SCENARIO = "natural_elec"
FUELS = ["electricity", "natural_gas", "propane", "fuel_oil"]
OUTPUTS_FILEPATH = "./outputs_combined/scenarios/{}".format(SCENARIO)


class ScenarioCreator:
    """
    Create scenario for a parcel and tally total energy usages
    """

    def __init__(
            self,
            sim_settings_filepath: str,
            building_config_filepath: str,
            utility_network_config_filepath: str,
            scenario_mapping_filepath: str,
            write_building_energy_timeseries: bool = False
    ):
        self._sim_settings_filepath = sim_settings_filepath
        self._building_config_filepath = building_config_filepath
        self._utility_network_config_filepath = utility_network_config_filepath
        self._scenario_mapping_filepath = scenario_mapping_filepath
        self.write_building_energy_timeseries: bool = write_building_energy_timeseries

        self.sim_config: dict = {}
        self._years_vec: List[int] = []
        self.scenario_mapping: List[dict] = []
        self.buildings_config: dict = {}
        self.buildings: Dict[str, Building] = {}
        self.utility_network: UtilityNetwork = None

    def create_scenario(self):
        self.get_sim_settings()
        self._years_vec = self._get_years_vec()
        self.get_scenario_mapping()
        print("Creating buildings...")
        self.create_building()
        print("Creatingy utility network...")
        self.create_utility_network()
        self._write_buildings_outputs()
        self._get_utility_network_outputs()

    def get_sim_settings(self) -> None:
        """
        Read in simulation settings
        """
        with open(self._sim_settings_filepath) as f:
            data = json.load(f)
        self.sim_config = data

    def _get_years_vec(self) -> List[int]:
        return list(range(
            self.sim_config.get("sim_start_year", 2020),
            self.sim_config.get("sim_end_year", 2050)
        ))

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
            building.write_building_cost_info()
            if self.write_building_energy_timeseries:
                building.write_building_energy_info()
            self.buildings[building.building_id] = building

    def _write_buildings_outputs(self) -> None:
        """
        Write output tables from all buildings
        """
        years_vec = pd.Index(data=self._years_vec, name="year")

        # ---Is Retrofit Vec---
        all_dfs = []
        for building_id, building in self.buildings.items():
            df = pd.DataFrame({"year": years_vec, "is_retrofit": building._is_retrofit_vec})
            df.loc[:, "building_id"] = building_id
            all_dfs.append(df)
        all_dfs = pd.concat(all_dfs)
        all_dfs.to_csv(os.path.join(OUTPUTS_FILEPATH, "is_retrofit_vec_table.csv"), index=False)

        # ---Retrofit year---
        all_dfs = []
        for building_id, building in self.buildings.items():
            df = pd.DataFrame({"year": years_vec, "retrofit_year": building._retrofit_vec})
            df.loc[:, "building_id"] = building_id
            all_dfs.append(df)
        all_dfs = pd.concat(all_dfs)
        all_dfs.to_csv(os.path.join(OUTPUTS_FILEPATH, "retrofit_year.csv"), index=False)

        # ---Retrofit cost---
        all_dfs = []
        for building_id, building in self.buildings.items():
            df = pd.DataFrame({
                "year": years_vec,
                "retrofit_cost": building._get_retrofit_cost_vec()
            })
            df.loc[:, "building_id"] = building_id
            all_dfs.append(df)
        all_dfs = pd.concat(all_dfs)
        all_dfs.to_csv(os.path.join(OUTPUTS_FILEPATH, "retrofit_cost.csv"), index=False)

        # ---Book value---
        all_dfs = []
        for building_id, building in self.buildings.items():
            # ---Replacement asset book value---
            df = pd.DataFrame({
                "year": years_vec,
                "book_val": building._get_retrofit_book_value_vec()
            })
            df.loc[:, "building_id"] = building_id
            df.loc[:, "existing_or_retrofit"] = "retrofit"
            all_dfs.append(df)

            # ---Existing book val---
            df = pd.DataFrame({
                "year": years_vec,
                "book_val": building._get_exising_book_val_vec()
            })
            df.loc[:, "building_id"] = building_id
            df.loc[:, "existing_or_retrofit"] = "existing"
            all_dfs.append(df)
        all_dfs = pd.concat(all_dfs)
        all_dfs.to_csv(os.path.join(OUTPUTS_FILEPATH, "book_val.csv"), index=False)

        # ---Existing stranded val---
        all_dfs = []
        for building_id, building in self.buildings.items():
            df = pd.DataFrame({
                "year": years_vec,
                "existing_stranded_val": building._get_exising_stranded_val_vec()
            })
            df.loc[:, "building_id"] = building_id
            all_dfs.append(df)
        all_dfs = pd.concat(all_dfs)
        all_dfs.to_csv(os.path.join(OUTPUTS_FILEPATH, "existing_stranded_val.csv"), index=False)

        # ---Energy use---
        building_energy_usage = {
            building_id: building._calc_annual_energy_consump()
            for building_id, building in self.buildings.items()
        }

        all_dfs = []
        for building_id, building_consumptions in building_energy_usage.items():
            for fuel in FUELS:
                df = pd.DataFrame({"year": years_vec, "consumption": building_consumptions[fuel]})
                df.loc[:, "asset_id"] = building_id
                df.loc[:, "energy_type"] = fuel
                all_dfs.append(df)

        xmfr_energy_usage = {
            xmfr.asset_id: list(xmfr.annual_total_energy_use.values())
            for xmfr in self.utility_network.elec_transformers
        }

        for asset_id, elec_consumption in xmfr_energy_usage.items():
            df = pd.DataFrame({"year": years_vec, "consumption": elec_consumption})
            df.loc[:, "asset_id"] = asset_id
            df.loc[:, "energy_type"] = "electricity"
            all_dfs.append(df)

        all_dfs = pd.concat(all_dfs)
        all_dfs.to_csv(os.path.join(OUTPUTS_FILEPATH, "energy_consumption.csv"), index=False)

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
            all_dfs.append(df)

        all_dfs = pd.concat(all_dfs)
        all_dfs.to_csv(os.path.join(OUTPUTS_FILEPATH, "peak_consump.csv"), index=False)

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
                df.loc[:, "building_id"] = building_id
                df.loc[:, "energy_type"] = fuel
                all_dfs.append(df)
        all_dfs = pd.concat(all_dfs)
        all_dfs.to_csv(os.path.join(OUTPUTS_FILEPATH, "consumption_costs.csv"), index=False)

        # ---Building fuel---
        all_dfs = []
        for building_id, building in self.buildings.items():
            df = pd.DataFrame({"year": years_vec, "fuel_type": building._fuel_type})
            df.loc[:, "building_id"] = building_id
            all_dfs.append(df)
        all_dfs = pd.concat(all_dfs)
        all_dfs.to_csv(os.path.join(OUTPUTS_FILEPATH, "fuel_type.csv"), index=False)

        # ---Methane leaks---
        all_dfs = []
        # Building leaks
        for building_id, building in self.buildings.items():
            df = pd.DataFrame({"year": years_vec, "leaks": building._methane_leaks})
            df.loc[:, "asset_id"] = building_id
            all_dfs.append(df)

        # Gas service leaks
        for service in self.utility_network.gas_services:
            df = pd.DataFrame({
                "year": years_vec,
                "leaks": service.annual_total_leakage
            })
            df.loc[:, "asset_id"] = service.asset_id
            all_dfs.append(df)

        # Gas main leaks
        for main in self.utility_network.gas_mains:
            df = pd.DataFrame({
                "year": years_vec,
                "leaks": main.annual_total_leakage
            })
            df.loc[:, "asset_id"] = main.asset_id
            all_dfs.append(df)
        all_dfs = pd.concat(all_dfs)
        all_dfs.to_csv(os.path.join(OUTPUTS_FILEPATH, "methane_leaks.csv"), index=False)

        # ---Combustion emissions---
        all_dfs = []
        for building_id, building in self.buildings.items():
            for fuel in FUELS:
                df = pd.DataFrame({
                    "year": years_vec,
                    "consumption_emissions": building._combustion_emissions[fuel]
                })
                df.loc[:, "building_id"] = building_id
                df.loc[:, "energy_type"] = fuel
                all_dfs.append(df)
        all_dfs = pd.concat(all_dfs)
        all_dfs.to_csv(os.path.join(OUTPUTS_FILEPATH, "consumption_emissions.csv"), index=False)

    def create_utility_network(self):
        """
        Create the utility network based on the input config
        """
        self.utility_network = UtilityNetwork(
            self._utility_network_config_filepath, self.sim_config, self.buildings
        )

        self.utility_network.populate_utility_network()

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
