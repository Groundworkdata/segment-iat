"""
Integration tests for the ScenarioCreator
"""
import os
import unittest

import pandas as pd

from scenario_creator.create_scenario import ScenarioCreator


class TestScenarioCreator(unittest.TestCase):
    def setUp(self):
        sim_settings_filepath = "tests_integration/test_data/simulation_settings_config.json"
        building_config_filepath = "tests_integration/test_data/doer_sf_accelerated-elec.json"
        utility_network_config_filepath = "tests_integration/test_data/utility_network_config.json"
        scenario_mapping_filepath = "tests_integration/test_data/scenario_mapping.json"
        write_building_energy_timeseries = False

        self.files = [
            "book_val.csv",
            "consumption_costs.csv",
            "consumption_emissions.csv",
            "energy_consumption.csv",
            "fuel_type.csv",
            "is_retrofit_vec_table.csv",
            "methane_leaks.csv",
            "peak_consump.csv",
            "retrofit_cost.csv",
            "retrofit_year.csv",
            "stranded_val.csv"
        ]

        self.scenario_creator = ScenarioCreator(
            sim_settings_filepath,
            building_config_filepath,
            utility_network_config_filepath,
            scenario_mapping_filepath,
            write_building_energy_timeseries
        )

    def test_create_scenario(self):
        self.scenario_creator.create_scenario()

        for i in self.files:
            output = pd.read_csv(os.path.join("./outputs_combined/scenarios/accelerated_elec", i))
            expected = pd.read_csv(os.path.join("./tests_integration/test_data/expected_outputs", i))

            pd.testing.assert_frame_equal(
                output,
                expected
            )

    def tearDown(self):
        for i in self.files:
            filepath = os.path.join("./outputs_combined/scenarios/accelerated_elec", i)
            if os.path.exists(filepath):
                os.remove(os.path.join(filepath))
