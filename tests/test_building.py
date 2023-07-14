"""
Unit tests for the Building module
"""
import datetime
import json
import os
import unittest
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd

from buildings.building import Building
from end_uses.building_end_uses.stove import Stove


class TestBuilding(unittest.TestCase):
    def setUp(self):
        self.building_params = {
            "building_id": "F_753646_2717355",
            "resstock_id": -1,
            "retrofit_year": 2041,
            "parcel_id": "F_753646_2717355",
            "original_fuel_type": "natural_gas",
            "retrofit_fuel_type": "hybrid_gas",
            "end_uses": [
                {
                    "end_use": "stove",
                    "existing_type": "LEGACY.STOVE",
                    "replacement_type": "HYBRID.STOVE",
                    "size": "SMALL",
                    "original_energy_source": "",
                    "replacement_cost_dollars_year": 2022,
                    "existing_install_year": 2018,
                    "replacement_year": 2041,
                    "lifetime": 30,
                    "replacement_lifetime": 30
                },
                {
                    "end_use": "clothes_dryer",
                    "existing_type": "LEGACY.DRYER",
                    "replacement_type": "HYBRID.DRYER",
                    "size": "SMALL",
                    "original_energy_source": "",
                    "replacement_cost_dollars_year": 2022,
                    "existing_install_year": 2018,
                    "replacement_year": 2041,
                    "lifetime": 30,
                    "replacement_lifetime": 30
                },
                {
                    "end_use": "domestic_hot_water",
                    "existing_type": "LEGACY.DHW",
                    "replacement_type": "HYBRID.DHW",
                    "size": "SMALL",
                    "original_energy_source": "",
                    "replacement_cost_dollars_year": 2022,
                    "existing_install_year": 2018,
                    "replacement_year": 2041,
                    "lifetime": 30,
                    "replacement_lifetime": 30
                },
                {
                    "end_use": "hvac",
                    "existing_type": "LEGACY.HVAC",
                    "replacement_type": "HYBRID.HVAC",
                    "size": "SMALL",
                    "original_energy_source": "",
                    "replacement_cost_dollars_year": 2022,
                    "existing_install_year": 2018,
                    "replacement_year": 2041,
                    "lifetime": 30,
                    "replacement_lifetime": 30
                }
            ],
            "retrofit_size": "small",
            "building_level_costs": {},
            "resstock_metadata": {},
            "resstock_overwrite": True,
            "reference_consump_filepath": "./config_files/buildings/MF_Existing_GAS.csv",
            "retrofit_consump_filepath": "./config_files/buildings/MF_Hybrid_GAS.csv",
            "load_scaling_factor": 2.25
        }

        self.sim_settings = {
            "sim_start_year": 2020,
            "sim_end_year": 2030,
            "decarb_scenario": "continued_gas",
            "replacement_year": 2025
        }

        self.scenario_mapping = [{
            "description": "hybrid_gas",
            "insulation": "none",
            "heat_pump": 5,
            "heating_fuel": "existing",
            "replacement_fuel": "existing",
            "hvac_resstock_scenario": 5,
            "dhw_resstock_scenario": 6,
            "dryer_resstock_scenario": 5,
            "range_resstock_scenario": 5,
            "range_retrofit_fuel": "existing",
            "hvac": 10,
            "main_resstock_retrofit_scenario": 5,
            "resstock_scenarios": [5, 6]
        }]

        self.building = Building(
            self.building_params,
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

    def test_get_years_vec(self):
        self.building._get_years_vec()

        self.assertListEqual(
            list(range(2020, 2030)),
            self.building.years_vec
        )

        self.assertListEqual(
            [
                pd.Timestamp(datetime.datetime(2018, 1, 1) + datetime.timedelta(seconds=60*60*i))
                for i in range(8760)
            ],
            self.building._year_timestamps.to_list()
        )

    def test_get_building_id(self):
        self.building._get_building_id()

        self.assertEqual(self.building.building_id, "F_753646_2717355")

    @patch("buildings.building.Building._get_resstock_scenario")
    def test_get_resstock_buildings(self, mock_get_resstock_scenario: Mock):
        mock_get_resstock_scenario.return_value = "resstock_scenario"
        self.building.retrofit_params = self.scenario_mapping[0]

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
            "MA", 30, -1
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
                "out.electricity.heating_hp_bkup.energy_consumption": {},
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
            "out.electricity.heating_hp_bkup.energy_consumption": {},
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

    #TODO: Fix after standardizing cost inputs
    @unittest.skip
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

    @unittest.skip
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
            [],
            custom_baseline_energy=pd.DataFrame(),
            custom_retrofit_energy=pd.DataFrame(),
            **{
                "end_use": "stove",
                "replacement_config": "tests/input_data/stoves/elec_stove_config.json",
            }
        )

    def test_calc_total_custom_baseline(self):
        self.building.baseline_consumption = pd.DataFrame({
            "out.electricity.range_oven.energy_consumption": {1: 1, 2: 2, 3: 3},
            "out.natural_gas.range_oven.energy_consumption": {1: 0, 2: 20, 3: 23},
            "out.electricity.heating.energy_consumption": {1: 0, 2: 0, 3: 1},
            "out.natural_gas.clothes_dryer.energy_consumption": {1: 30, 2: 2, 3: 3},
        })

        self.building._calc_total_custom_baseline()

        pd.testing.assert_frame_equal(
            self.building.baseline_consumption,
            pd.DataFrame({
                "out.electricity.range_oven.energy_consumption": {1: 1, 2: 2, 3: 3},
                "out.natural_gas.range_oven.energy_consumption": {1: 0, 2: 20, 3: 23},
                "out.electricity.heating.energy_consumption": {1: 0, 2: 0, 3: 1},
                "out.natural_gas.clothes_dryer.energy_consumption": {1: 30, 2: 2, 3: 3},
                "out.electricity.total.energy_consumption": {1: 1, 2: 2, 3: 4},
                "out.natural_gas.total.energy_consumption": {1: 30, 2: 22, 3: 26},
                "out.propane.total.energy_consumption": {1: 0, 2: 0, 3: 0},
                "out.fuel_oil.total.energy_consumption": {1: 0, 2: 0, 3: 0},
                "out.total.energy_consumption": {1: 31, 2: 24, 3: 30},
            }),
            check_dtype=False
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

    def test_calc_building_costs(self):
        self.building.building_params = {
            "building_level_costs": {
                "retrofit_adder": {"small": 10, "medium": 25, "large": 100,},
            },
            "retrofit_size": "large",
        }

        self.building._retrofit_vec = [0, 0, 0, 1, 0]

        self.assertListEqual(
            self.building._calc_building_costs(),
            [0, 0, 0, 100, 0]
        )

    def test_get_replacement_vec(self):
        self.building.building_params["retrofit_year"] = 2035
        self.building.years_vec = list(range(2020, 2040))

        expected_vec = [False for i in range(20)]
        expected_vec[15] = True

        self.assertListEqual(
            self.building._get_replacement_vec(),
            expected_vec
        )

    #TODO: Finalize standard cost data inputs and update
    @unittest.skip
    def test_calc_building_utility_costs(self):
        years_vec = [2020, 2021, 2022, 2023]
        self.building.years_vec = years_vec

        utility_costs = {
            "electricity": [(15/293) * (1 + 0.01) ** (i-2022) for i in years_vec],
            "natural_gas": [(45/293) * (1 + 0.01) ** (i-2022) for i in years_vec],
            "fuel_oil": [(20/293) * (1 + 0.01) ** (i-2022) for i in years_vec],
        }

        utility_costs["propane"] = (
            np.array(utility_costs["electricity"]) * (0.8 / 3)
            + np.array(utility_costs["natural_gas"]) * 0.3
        ).tolist()

        self.building._retrofit_vec = [False, True, False, False]

        timeseries_index = pd.date_range(start="1/1/2018", periods=4, freq="1H")

        self.building.baseline_consumption = pd.DataFrame({
            "out.electricity.total.energy_consumption": {0: 10, 1: 20, 3: 23, 4: 0},
            "out.natural_gas.total.energy_consumption": {0: 6, 1: 0, 3: 40, 4: 0},
            "out.propane.total.energy_consumption": {0: 0, 1: 0, 3: 0, 4: 0},
            "out.fuel_oil.total.energy_consumption": {0: 0, 1: 0, 3: 0, 4: 0},
        }).set_index(timeseries_index)

        self.building.retrofit_consumption = pd.DataFrame({
            "out.electricity.total.energy_consumption": {0: 12, 1: 20, 3: 23, 4: 0},
            "out.natural_gas.total.energy_consumption": {0: 0, 1: 0, 3: 0, 4: 0},
            "out.propane.total.energy_consumption": {0: 8, 1: 0, 3: 50, 4: 0},
            "out.fuel_oil.total.energy_consumption": {0: 0, 1: 0, 3: 0, 4: 0},
        }).set_index(timeseries_index)

        expected_costs = {
            "electricity": [
                53 * utility_costs["electricity"][0],
                55 * utility_costs["electricity"][1],
                55 * utility_costs["electricity"][2],
                55 * utility_costs["electricity"][3]
            ],
            "natural_gas": [
                46 * utility_costs["natural_gas"][0],
                0.0,
                0.0,
                0.0,
            ],
            "propane": [
                0.0,
                58 * utility_costs["propane"][1],
                58 * utility_costs["propane"][2],
                58 * utility_costs["propane"][3],
            ],
            "fuel_oil": [0.0, 0.0, 0.0, 0.0]
        }

        self.assertDictEqual(
            expected_costs,
            self.building._calc_building_utility_costs()
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

        self.building.baseline_consumption.index = pd.date_range(
            start="1/1/2023", freq="15T", periods=4
        )
        self.building.retrofit_consumption.index = pd.date_range(
            start="1/1/2023", freq="15T", periods=4
        )

        self.building._get_building_id()
        self.building.write_building_energy_info(freq=15)

        expected_baseline_csv = "./outputs/F_753646_2717355_baseline_consump.csv"
        expected_retrofit_csv = "./outputs/F_753646_2717355_retrofit_consump.csv"

        self.assertTrue(os.path.exists(expected_baseline_csv))
        self.assertTrue(os.path.exists(expected_retrofit_csv))

        written_baseline = pd.read_csv(expected_baseline_csv, index_col=0)
        written_retrofit = pd.read_csv(expected_retrofit_csv, index_col=0)

        # FIXME: Need more robust way of testing datetimes here
        pd.testing.assert_frame_equal(
            self.building.baseline_consumption.reset_index(drop=True),
            written_baseline.reset_index(drop=True)
        )
        pd.testing.assert_frame_equal(
            self.building.retrofit_consumption.reset_index(drop=True),
            written_retrofit.reset_index(drop=True)
        )

        os.remove(expected_baseline_csv)
        os.remove(expected_retrofit_csv)
