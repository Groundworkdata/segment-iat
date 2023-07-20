"""
Unit tests for ScenarioCreator class
"""
import json
import unittest
from unittest.mock import Mock, patch

from scenario_creator.create_scenario import ScenarioCreator


class TestScenarioCreator(unittest.TestCase):
    def setUp(self):
        self.scenario_creator = ScenarioCreator(
            "tests/input_data/sim_settings_config.json",
            write_building_energy_timeseries=True
        )

    @patch("scenario_creator.create_scenario.ScenarioCreator._get_utility_network_outputs")
    @patch("scenario_creator.create_scenario.ScenarioCreator._write_outputs")
    @patch("scenario_creator.create_scenario.ScenarioCreator._create_utility_network")
    @patch("scenario_creator.create_scenario.ScenarioCreator._create_building")
    @patch("scenario_creator.create_scenario.ScenarioCreator._get_scenario_mapping")
    @patch("scenario_creator.create_scenario.ScenarioCreator._get_years_vec")
    @patch("scenario_creator.create_scenario.ScenarioCreator._set_outputs_path")
    @patch("scenario_creator.create_scenario.ScenarioCreator._get_decarb_scenario")
    @patch("scenario_creator.create_scenario.ScenarioCreator._get_sim_settings")
    def test_create_scenario(
        self,
        mock_get_sim_settings: Mock,
        mock_get_decarb_scenario: Mock,
        mock_set_outputs_path: Mock,
        mock_get_years_vec: Mock,
        mock_get_scenario_mapping: Mock,
        mock_create_building: Mock,
        mock_create_utility_network: Mock,
        mock_write_outputs: Mock,
        mock_get_utility_network_outputs: Mock
    ):
        mock_get_sim_settings.return_value = {"sim_settings": 1}
        mock_get_decarb_scenario.return_value = "decarb_scenario"
        mock_set_outputs_path.return_value = "outputs_path"
        mock_get_years_vec.return_value = [1, 2, 3]

        self.scenario_creator.create_scenario()

        mock_get_sim_settings.assert_called_once()
        self.assertDictEqual(self.scenario_creator._sim_config, {"sim_settings": 1})
        mock_get_decarb_scenario.assert_called_once()
        self.assertEqual(self.scenario_creator._decarb_scenario, "decarb_scenario")
        mock_set_outputs_path.assert_called_once()
        self.assertEqual(self.scenario_creator._outputs_path, "outputs_path")
        mock_get_years_vec.assert_called_once()
        self.assertListEqual(self.scenario_creator._years_vec, [1, 2, 3])
        mock_get_scenario_mapping.assert_called_once()
        mock_create_building.assert_called_once()
        mock_create_utility_network.assert_called_once()
        mock_write_outputs.assert_called_once()
        mock_get_utility_network_outputs.assert_called_once()

    def test_get_sim_settings(self):
        self.assertDictEqual(
            self.scenario_creator._get_sim_settings(),
            {
                "sim_start_year": 2020,
                "sim_end_year": 2040,
                "decarb_scenario": "continued_gas",
                "buildings_config_filepath": "./tests/input_data/building_config.json",
                "utility_network_config_filepath": "./tests/input_data/whatever.json"
            }
        )

    def test_get_decarb_scenario(self):
        self.scenario_creator._sim_config = {"decarb_scenario": "continued_gas"}

        self.assertEqual(
            self.scenario_creator._get_decarb_scenario(),
            "continued_gas"
        )

        self.scenario_creator._sim_config = {"decarb_scenario": "whatever"}

        with self.assertRaises(ValueError):
            self.scenario_creator._get_decarb_scenario()

    def test_set_outputs_path(self):
        self.scenario_creator._decarb_scenario = "hybrid_gas"

        self.assertEqual(
            self.scenario_creator._set_outputs_path(),
            "./outputs_combined/scenarios/hybrid_gas"
        )

    def test_get_years_vec(self):
        self.assertListEqual(
            list(range(2020, 2050)),
            self.scenario_creator._get_years_vec()
        )

    def test_get_scenario_mapping(self):
        self.scenario_creator._get_scenario_mapping()

        with open("./config_files/scenario_mapping.json") as f:
            expected = json.load(f)

        self.assertListEqual(
            self.scenario_creator._scenario_mapping,
            expected
        )

    @patch("scenario_creator.create_scenario.Building")
    def test_create_building(self, mock_building: Mock):
        mock_building_instance = Mock()
        mock_building_instance.building_id = "b1"
        mock_building.return_value = mock_building_instance
        self.scenario_creator._sim_config = {
            "buildings_config_filepath": "./tests/input_data/building_config.json"
        }

        self.scenario_creator._scenario_mapping = "mapping"

        self.scenario_creator._create_building()

        expected_config = [{
            "building_id": "building001",
            "resstock_id": 1,
            "retrofit_year": 2027,
            "resstock_metadata": "resstock_metadata",
            "end_uses": [
                {
                    "end_use": "stove",
                    "original_energy_source": "gas",
                    "original_config": "./stoves/gas_stove_config.json",
                    "replacement_config": "./stoves/elec_stove_config.json"
                }
            ]
        }]

        self.assertListEqual(
            self.scenario_creator._buildings_config,
            expected_config
        )

        mock_building.assert_called_once_with(
            expected_config[0],
            {"buildings_config_filepath": "./tests/input_data/building_config.json"},
            "mapping"
        )

        mock_building_instance.populate_building.assert_called_once()
        mock_building_instance.write_building_energy_info.assert_called_once()

        self.assertDictEqual(
            self.scenario_creator.buildings,
            {"b1": mock_building_instance}
        )

    @patch("scenario_creator.create_scenario.UtilityNetwork")
    def test_create_utility_network(self, mock_utility_network: Mock):
        self.scenario_creator._sim_config = {
            "utility_network_config_filepath": "path-to-config"
        }
        self.scenario_creator.buildings = "buildings"
        utility_instance = Mock()
        mock_utility_network.return_value = utility_instance

        self.scenario_creator._create_utility_network()

        mock_utility_network.assert_called_once_with(
            "path-to-config",
            {"utility_network_config_filepath": "path-to-config"},
            "buildings"
        )

        self.assertEqual(
            self.scenario_creator.utility_network,
            utility_instance
        )

        utility_instance.populate_utility_network.assert_called_once()
