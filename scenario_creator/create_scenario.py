"""
Creates a scenario based on input values
"""
import json
from typing import Dict, List

import pandas as pd

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
        self._years_vec: List[int] = []
        self.scenario_mapping: List[dict] = []
        self.buildings_config: dict = {}
        self.buildings: Dict[str, Building] = {}
        self.utility_network: UtilityNetwork = None

    def create_scenario(self):
        self.get_sim_settings()
        self._years_vec = self._get_years_vec()
        self.get_scenario_mapping()
        self.create_building()
        self._write_buildings_outputs()
        print("Creating Utility Network")
        self.create_utility_network()
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
            building.write_building_energy_info()
            building.write_building_cost_info()
            self.buildings[building.building_id] = building

    def _write_buildings_outputs(self) -> None:
        """
        Write output tables from all buildings
        """
        # Start with _is_retrofit_vec
        #TODO: What orientation is better? Years are rows or cols (default is rows)?
        output_index = pd.Index(data=self._years_vec, name="year")

        # ---Is Retrofit Vec---
        is_retrofit_vec_table = pd.DataFrame(
            {
                building_id: building._is_retrofit_vec
                for building_id, building in self.buildings.items()
            },
            index=output_index
        )
        is_retrofit_vec_table.to_csv("./outputs/is_retrofit_vec_table.csv")

        # ---Asset replacement cost---
        retrofit_cost_table = pd.DataFrame(
            {
                building_id: building._get_retrofit_cost_vec()
                for building_id, building in self.buildings.items()
            },
            index=output_index
        )
        retrofit_cost_table.to_csv("./outputs/retrofit_cost_table.csv")

        # ---Replacement asset book value---
        retrofit_book_val_table = pd.DataFrame(
            {
                building_id: building._get_retrofit_book_value_vec()
                for building_id, building in self.buildings.items()
            },
            index=output_index
        )
        retrofit_book_val_table.to_csv("./outputs/retrofit_book_val_table.csv")

        # ---Existing book val
        existing_book_val_table = pd.DataFrame(
            {
                building_id: building._get_exising_book_val_vec()
                for building_id, building in self.buildings.items()
            },
            index=output_index
        )
        existing_book_val_table.to_csv("./outputs/existing_book_val_table.csv")

        # ---Existing stranded val---
        existing_stranded_val_table = pd.DataFrame(
            {
                building_id: building._get_exising_stranded_val_vec()
                for building_id, building in self.buildings.items()
            },
            index=output_index
        )
        existing_stranded_val_table.to_csv("./outputs/existing_stranded_val_table.csv")

        # ---Building energy use---
        building_energy_usage = {
            building_id: building._calc_annual_energy_consump()
            for building_id, building in self.buildings.items()
        }

        fuels = ["electricity", "natural_gas", "propane", "fuel_oil"]

        for fuel in fuels:
            consump_table = pd.DataFrame(
                {
                    building_id: usage[fuel]
                    for building_id, usage in building_energy_usage.items()
                },
                index=output_index
            )
            consump_table.to_csv("./outputs/{}_consump.csv".format(fuel))

        # ---Building utility costs---
        building_util_costs = {
            building_id: building._calc_building_utility_costs()
            for building_id, building in self.buildings.items()
        }

        for fuel in fuels:
            cost_table = pd.DataFrame(
                {
                    building_id: costs[fuel]
                    for building_id, costs in building_util_costs.items()
                },
                index=output_index
            )
            cost_table.to_csv("./outputs/{}_utility_costs.csv".format(fuel))

        # ---Building fuel---
        fuel_table = pd.DataFrame(
            {
                building_id: building._fuel_type
                for building_id, building in self.buildings.items()
            },
            index=output_index
        )
        fuel_table.to_csv("./outputs/fuel_type.csv")

        # ---Methane leaks---
        leaks_table = pd.DataFrame(
            {
                building_id: building._methane_leaks
                for building_id, building in self.buildings.items()
            },
            index=output_index
        )
        leaks_table.to_csv("./outputs/methane_leaks_table.csv")

        # ---Combustion emissions---
        for fuel in fuels:
            combustion_emissions = pd.DataFrame(
                {
                    building_id: building._combustion_emissions[fuel]
                    for building_id, building in self.buildings.items()
                },
                index=output_index
            )
            combustion_emissions.to_csv("./outputs/{}_combustion_emissions.csv".format(fuel))

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
        print(
            pd.DataFrame(
                {
                    xmfr.asset_id: xmfr.overloading_ratio 
                    for xmfr in self.utility_network.elec_transformers
                }
            )
        )
