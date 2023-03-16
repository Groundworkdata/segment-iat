"""
Unit tests for the Building module
"""

#TODO: Integration tests
import json
import os
import unittest
from unittest.mock import Mock, patch

import pandas as pd

from buildings.building import Building
from end_uses.building_end_uses.stove import Stove


class TestBuilding(unittest.TestCase):
    def setUp(self):
        self._building_config_filepath = "tests/input_data/building_config.json"

        with open(self._building_config_filepath) as f:
            data = json.load(f)
        self.building_params = data

        self.sim_settings = {
            "sim_start_year": 2020,
            "sim_end_year": 2040,
            "decarb_scenario": 3,
        }

        scenario_mapping_filepath = "./config_files/scenario_mapping.json"

        with open(scenario_mapping_filepath) as f:
            data = json.load(f)
        self.scenario_mapping = data

        self.building = Building(
            self.building_params[0],
            self.sim_settings,
            self.scenario_mapping
        )

    @unittest.skip
    def test_populate_building(self):
        self.building.populate_building()

        self.assertEqual(
            list(self.building.end_uses.keys()),
            ["stove"]
        )

        self.assertEqual(
            list(self.building.end_uses["stove"].keys()),
            ["stove1", "stove2"]
        )

        self.assertEqual(type(self.building.end_uses["stove"]["stove1"]), Stove)
        self.assertEqual(type(self.building.end_uses["stove"]["stove2"]), Stove)

    @unittest.skip
    def test_sum_end_use_figures(self):
        mock_stove_1 = Mock()
        mock_stove_1.install_cost = [100, 0, 0, 0, 0]

        mock_stove_2 = Mock()
        mock_stove_2.install_cost = [0, 0, 70, 0, 0]

        self.building.end_uses = {
            "stove": {
                "stove1": mock_stove_1,
                "stove2": mock_stove_2
            }
        }

        self.building.years_vec = list(range(2025, 2030))

        pd.testing.assert_frame_equal(
            pd.DataFrame({
                "stove1_install_cost": {
                    2025: 100,
                    2026: 0,
                    2027: 0,
                    2028: 0,
                    2029: 0
                },
                "stove2_install_cost": {
                    2025: 0,
                    2026: 0,
                    2027: 70,
                    2028: 0,
                    2029: 0
                },
                "total_install_cost": {
                    2025: 100,
                    2026: 0,
                    2027: 70,
                    2028: 0,
                    2029: 0
                }
            }),
            self.building._sum_end_use_figures("install_cost")
        )

    def test_get_building_id(self):
        self.building._get_building_id()

        self.assertEqual(self.building.building_id, "building001")

    @patch("buildings.building.Building._get_resstock_scenario")
    def test_get_resstock_buildings(self, mock_get_resstock_scenario: Mock):
        mock_get_resstock_scenario.return_value = "resstock_scenario"

        self.building._get_resstock_buildings()

        self.assertDictEqual(
            self.building.resstock_scenarios,
            {
                0: "resstock_scenario",
                5: "resstock_scenario",
                6: "resstock_scenario",
            }
        )

    @patch("buildings.building.Building.resstock_timeseries_connector")
    def test_get_resstock_scenario(self, mock_resstock_timeseries_connector: Mock):
        mock_resstock_timeseries_connector.return_value = "connected"

        self.assertEqual(
            self.building._get_resstock_scenario(30),
            "connected"
        )

        mock_resstock_timeseries_connector.assert_called_once_with(
            "MA", 30, 1
        )

    def test_get_baseline_consumptions(self):
        self.building.resstock_scenarios = {
            0: pd.DataFrame({
                "out.site_energy.total.energy_consumption": {},
                "out.electricity.total.energy_consumption": {1: 100, 2: 100, 3: 400, 5: 150},
                "out.natural_gas.total.energy_consumption": {1: 10, 2: 20, 3: 60, 5: 30},
                "out.fuel_oil.total.energy_consumption": {1: 0, 2: 0, 3: 0, 5: 0},
                "out.propane.total.energy_consumption": {1: 0, 2: 0, 3: 0, 5: 0},
                "out.electricity.range_oven.energy_consumption": {1: 0, 2: 0, 3: 0, 5: 0},
                "out.natural_gas.range_oven.energy_consumption": {1: 2, 2: 0, 3: 1, 5: 0.5},
                "out.propane.range_oven.energy_consumption": {},
                "out.electricity.clothes_dryer.energy_consumption": {},
                "out.natural_gas.clothes_dryer.energy_consumption": {},
                "out.propane.clothes_dryer.energy_consumption": {},
                "out.electricity.hot_water.energy_consumption": {1: 20, 2: 25, 3: 40.2, 5: 0},
                "out.natural_gas.hot_water.energy_consumption": {},
                "out.propane.hot_water.energy_consumption": {},
                "out.fuel_oil.hot_water.energy_consumption": {},
                "out.electricity.heating.energy_consumption": {},
                "out.electricity.cooling.energy_consumption": {},
                "out.natural_gas.heating.energy_consumption": {},
                "out.natural_gas.heating_hp_bkup.energy_consumption": {},
                "out.propane.heating.energy_consumption": {},
                "out.propane.heating_hp_bkup.energy_consumption": {},
                "out.fuel_oil.heating.energy_consumption": {},
                "out.fuel_oil.heating_hp_bkup.energy_consumption": {},
                "some_other": {1: 1000, 2: 25, 3: 40.2, 5: 0.89},
            })
        }

        expected_baseline_consump = pd.DataFrame({
            "out.site_energy.total.energy_consumption": {},
            "out.electricity.total.energy_consumption": {1: 100, 2: 100, 3: 400, 5: 150},
            "out.natural_gas.total.energy_consumption": {1: 10, 2: 20, 3: 60, 5: 30},
            "out.fuel_oil.total.energy_consumption": {1: 0, 2: 0, 3: 0, 5: 0},
            "out.propane.total.energy_consumption": {1: 0, 2: 0, 3: 0, 5: 0},
            "out.electricity.range_oven.energy_consumption": {1: 0, 2: 0, 3: 0, 5: 0},
            "out.natural_gas.range_oven.energy_consumption": {1: 2, 2: 0, 3: 1, 5: 0.5},
            "out.propane.range_oven.energy_consumption": {},
            "out.electricity.clothes_dryer.energy_consumption": {},
            "out.natural_gas.clothes_dryer.energy_consumption": {},
            "out.propane.clothes_dryer.energy_consumption": {},
            "out.electricity.hot_water.energy_consumption": {1: 20, 2: 25, 3: 40.2, 5: 0},
            "out.natural_gas.hot_water.energy_consumption": {},
            "out.propane.hot_water.energy_consumption": {},
            "out.fuel_oil.hot_water.energy_consumption": {},
            "out.electricity.heating.energy_consumption": {},
            "out.electricity.cooling.energy_consumption": {},
            "out.natural_gas.heating.energy_consumption": {},
            "out.natural_gas.heating_hp_bkup.energy_consumption": {},
            "out.propane.heating.energy_consumption": {},
            "out.propane.heating_hp_bkup.energy_consumption": {},
            "out.fuel_oil.heating.energy_consumption": {},
            "out.fuel_oil.heating_hp_bkup.energy_consumption": {},
            "out.electricity.other.energy_consumption": {1: 80, 2: 75, 3: 359.8, 5: 150},
            "out.natural_gas.other.energy_consumption": {1: 8, 2: 20, 3: 59, 5: 29.5},
            "out.propane.other.energy_consumption": {1: 0, 2: 0, 3: 0, 5: 0},
            "out.fuel_oil.other.energy_consumption": {1: 0, 2: 0, 3: 0, 5: 0},
        })

        self.building._get_baseline_consumptions()

        pd.testing.assert_frame_equal(
            expected_baseline_consump,
            self.building.baseline_consumption,
            check_dtype=False
        )

    def test_get_retrofit_consumptions(self):
        pass

    @patch("buildings.building.Building._get_single_end_use")
    def test_create_end_uses(self, mock_get_single_end_use: Mock):
        mock_get_single_end_use.return_value = "my_stove"

        self.building._create_end_uses()

        self.assertDictEqual(
            self.building.end_uses,
            {"stove": "my_stove"}
        )

        mock_get_single_end_use.assert_called_once_with({
            "end_use": "stove",
            "original_energy_source": "gas",
            "original_config": "./stoves/gas_stove_config.json",
            "replacement_config": "./stoves/elec_stove_config.json"
        })

    @patch("buildings.building.Stove")
    def test_get_single_end_use(self, mock_stove: Mock):
        initialized_stove = Mock()
        mock_stove.return_value = initialized_stove

        params = {
            "end_use": "stove",
            "replacement_config": "tests/input_data/stoves/elec_stove_config.json",
            "original_energy_source": "gas",
        }

        single_end_use_return = self.building._get_single_end_use(params)

        self.assertEqual(
            single_end_use_return,
            initialized_stove
        )

        mock_stove.assert_called_once_with(
            "gas",
            {},
            self.scenario_mapping,
            3,
            "resstock_metadata",
            **{
                "asset_cost": 1500,
                "lifetime": 10,
                "removal_labor_time": 2,
                "labor_rate": 50,
                "misc_supplies_price": 75,
                "retail_markup": 0.18,
                "installation_labor_time": 1,
                "annual_cost_escalation": 0.01
            }
        )

    def test_calc_baseline_energy(self):
        stove = Mock()
        stove.baseline_energy_use = pd.DataFrame({
            "out.electricity.range_oven.energy_consumption": {1: 0, 2: 10, 3: 10, 4: 0},
            "out.natural_gas.range_oven.energy_consumption": {1: 0, 2: 0, 3: 0, 4: 0},
            "out.propane.range_oven.energy_consumption": {1: 0, 2: 0, 3: 0, 4: 0},
        })

        self.building.end_uses["stove"] = stove

        self.building.baseline_consumption = pd.DataFrame({
            "out.electricity.range_oven.energy_consumption": {1: 50, 2: 10, 3: 40, 4: 50},
            "out.natural_gas.range_oven.energy_consumption": {1: 0, 2: 20, 3: 0, 4: 0},
            "out.propane.range_oven.energy_consumption": {1: 0, 2: 0, 3: 0, 4: 10},
            "out.electricity.other.energy_consumption": {1: 0, 2: 0, 3: 0, 4: 10},
            "out.natural_gas.other.energy_consumption": {1: 0, 2: 0, 3: 0, 4: 10},
            "out.propane.other.energy_consumption": {1: 0, 2: 0, 3: 0, 4: 10},
            "out.fuel_oil.other.energy_consumption": {1: 0, 2: 0, 3: 0, 4: 0},
        })

        self.building._calc_baseline_energy()

        pd.testing.assert_frame_equal(
            self.building.baseline_consumption.sort_index(axis=1),
            pd.DataFrame({
                "out.electricity.range_oven.energy_consumption": {1: 50, 2: 10, 3: 40, 4: 50},
                "out.natural_gas.range_oven.energy_consumption": {1: 0, 2: 20, 3: 0, 4: 0},
                "out.propane.range_oven.energy_consumption": {1: 0, 2: 0, 3: 0, 4: 10},
                "out.electricity.other.energy_consumption": {1: 0, 2: 0, 3: 0, 4: 10},
                "out.natural_gas.other.energy_consumption": {1: 0, 2: 0, 3: 0, 4: 10},
                "out.propane.other.energy_consumption": {1: 0, 2: 0, 3: 0, 4: 10},
                "out.fuel_oil.other.energy_consumption": {1: 0, 2: 0, 3: 0, 4: 0},
                "out.electricity.range_oven.energy_consumption_update": {1: 0, 2: 10, 3: 10, 4: 0},
                "out.natural_gas.range_oven.energy_consumption_update": {1: 0, 2: 0, 3: 0, 4: 0},
                "out.propane.range_oven.energy_consumption_update": {1: 0, 2: 0, 3: 0, 4: 0},
                "out.electricity.total.energy_consumption_update": {1: 0, 2: 10, 3: 10, 4: 10},
                "out.natural_gas.total.energy_consumption_update": {1: 0, 2: 0, 3: 0, 4: 10},
                "out.propane.total.energy_consumption_update": {1: 0, 2: 0, 3: 0, 4: 10},
                "out.fuel_oil.total.energy_consumption_update": {1: 0, 2: 0, 3: 0, 4: 0},
            }).sort_index(axis=1)
        )

    def test_calc_retrofit_energy(self):
        stove = Mock()
        stove.retrofit_energy_use = pd.DataFrame({
            "out.electricity.range_oven.energy_consumption": {1: 20, 2: 30, 3: 10, 4: 0},
            "out.natural_gas.range_oven.energy_consumption": {1: 0, 2: 0, 3: 0, 4: 0},
            "out.propane.range_oven.energy_consumption": {1: 0, 2: 0, 3: 0, 4: 0},
        })

        self.building.end_uses["stove"] = stove

        self.building.retrofit_consumption = pd.DataFrame({
            "out.electricity.range_oven.energy_consumption": {1: 50, 2: 10, 3: 40, 4: 50},
            "out.natural_gas.range_oven.energy_consumption": {1: 0, 2: 20, 3: 0, 4: 0},
            "out.propane.range_oven.energy_consumption": {1: 0, 2: 0, 3: 0, 4: 10},
            "out.electricity.other.energy_consumption": {1: 0, 2: 0, 3: 0, 4: 10},
            "out.natural_gas.other.energy_consumption": {1: 0, 2: 0, 3: 0, 4: 10},
            "out.propane.other.energy_consumption": {1: 0, 2: 0, 3: 0, 4: 10},
            "out.fuel_oil.other.energy_consumption": {1: 0, 2: 0, 3: 0, 4: 0},
        })

        self.building._calc_retrofit_energy()

        pd.testing.assert_frame_equal(
            self.building.retrofit_consumption.sort_index(axis=1),
            pd.DataFrame({
                "out.electricity.range_oven.energy_consumption": {1: 50, 2: 10, 3: 40, 4: 50},
                "out.natural_gas.range_oven.energy_consumption": {1: 0, 2: 20, 3: 0, 4: 0},
                "out.propane.range_oven.energy_consumption": {1: 0, 2: 0, 3: 0, 4: 10},
                "out.electricity.other.energy_consumption": {1: 0, 2: 0, 3: 0, 4: 10},
                "out.natural_gas.other.energy_consumption": {1: 0, 2: 0, 3: 0, 4: 10},
                "out.propane.other.energy_consumption": {1: 0, 2: 0, 3: 0, 4: 10},
                "out.fuel_oil.other.energy_consumption": {1: 0, 2: 0, 3: 0, 4: 0},
                "out.electricity.range_oven.energy_consumption_update": {1: 20, 2: 30, 3: 10, 4: 0},
                "out.natural_gas.range_oven.energy_consumption_update": {1: 0, 2: 0, 3: 0, 4: 0},
                "out.propane.range_oven.energy_consumption_update": {1: 0, 2: 0, 3: 0, 4: 0},
                "out.electricity.total.energy_consumption_update": {1: 20, 2: 30, 3: 10, 4: 10},
                "out.natural_gas.total.energy_consumption_update": {1: 0, 2: 0, 3: 0, 4: 10},
                "out.propane.total.energy_consumption_update": {1: 0, 2: 0, 3: 0, 4: 10},
                "out.fuel_oil.total.energy_consumption_update": {1: 0, 2: 0, 3: 0, 4: 0},
            }).sort_index(axis=1)
        )

    def test_write_building_energy_info(self):
        self.building.baseline_consumption = pd.DataFrame({
            "out.electricity.total.energy_conumption": {0: 1, 1: 2, 3: 2, 4: 0},
            "out.natural_gas.total.energy_conumption": {0: 1, 1: 2, 3: 2, 4: 0},
            "out.propane.total.energy_conumption": {0: 1, 1: 2, 3: 2, 4: 0},
            "out.propane.stove.energy_conumption": {0: 1, 1: 2, 3: 2, 4: 0},
        })

        self.building.retrofit_consumption = pd.DataFrame({
            "out.electricity.total.energy_conumption": {0: 1, 1: 2, 3: 2, 4: 50},
            "out.natural_gas.total.energy_conumption": {0: 0, 1: 2, 3: 2, 4: 0},
            "out.propane.total.energy_conumption": {0: 1, 1: 6, 3: 2, 4: 0},
            "out.propane.stove.energy_conumption": {0: 1, 1: 2, 3: 2, 4: 0},
        })

        self.building._get_building_id()
        self.building.write_building_energy_info()

        expected_baseline_csv = "./outputs/building001_baseline_consump.csv"
        expected_retrofit_csv = "./outputs/building001_retrofit_consump.csv"

        self.assertTrue(os.path.exists(expected_baseline_csv))
        self.assertTrue(os.path.exists(expected_retrofit_csv))

        written_baseline = pd.read_csv(expected_baseline_csv, index_col=0)
        written_retrofit = pd.read_csv(expected_retrofit_csv, index_col=0)

        pd.testing.assert_frame_equal(self.building.baseline_consumption, written_baseline)
        pd.testing.assert_frame_equal(self.building.retrofit_consumption, written_retrofit)

        os.remove(expected_baseline_csv)
        os.remove(expected_retrofit_csv)
