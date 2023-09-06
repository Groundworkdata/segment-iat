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

        self.building = Building(
            self.building_params,
            self.sim_settings
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

    @patch("buildings.building.Stove")
    def test_get_single_end_use(self, mock_stove: Mock):
        initialized_stove = Mock()
        mock_stove.return_value = initialized_stove

        # Need to set because of issues testing pandas objects
        self.building.baseline_consumption = "baseline_consump"
        self.building.retrofit_consumption = "retrofit_consump"

        params = {
            "end_use": "stove",
            "replacement_config": "tests/input_data/stoves/elec_stove_config.json"
        }

        single_end_use_return = self.building._get_single_end_use(params)

        self.assertEqual(
            single_end_use_return,
            initialized_stove
        )

        mock_stove.assert_called_once_with(
            [],
            custom_baseline_energy="baseline_consump",
            custom_retrofit_energy="retrofit_consump",
            **{
                "end_use": "stove",
                "replacement_config": "tests/input_data/stoves/elec_stove_config.json"
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
