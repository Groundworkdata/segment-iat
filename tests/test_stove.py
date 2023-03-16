"""
Contains tests for the Stove end use
"""
import unittest

import pandas as pd

from end_uses.building_end_uses.stove import Stove


class TestStove(unittest.TestCase):
    def setUp(self):
        energy_source = "natural_gas"
        resstock_consumptions = {
            0: pd.DataFrame({
                "out.natural_gas.range_oven.energy_consumption": {
                    1: 1, 2: 2, 3: 0, 4: 1
                },
                "out.electricity.range_oven.energy_consumption": {
                    1: 0, 2: 0, 3: 0, 4: 0
                },
                "out.propane.range_oven.energy_consumption": {
                    1: 0, 2: 0, 3: 0, 4: 0
                },
            }),
            5: pd.DataFrame({
                "out.natural_gas.range_oven.energy_consumption": {
                    1: 1, 2: 2, 3: 0, 4: 1
                },
                "out.electricity.range_oven.energy_consumption": {
                    1: 0, 2: 0, 3: 0, 4: 0
                },
                "out.propane.range_oven.energy_consumption": {
                    1: 0, 2: 0, 3: 0, 4: 0
                },
            }),
            10: pd.DataFrame({
                "out.electricity.range_oven.energy_consumption": {
                    1: 10, 2: 15, 3: 0, 4: 10
                },
                "out.natural_gas.range_oven.energy_consumption": {
                    1: 0, 2: 0, 3: 0, 4: 0
                },
                "out.propane.range_oven.energy_consumption": {
                    1: 0, 2: 0, 3: 0, 4: 0
                },
            })
        }

        scenario_mapping = [
            {
                "range_resstock_scenario": 0,
                "range_retrofit_fuel": "existing",
                "resstock_scenarios": [0]
            },
            {},
            {},
            {
                "range_resstock_scenario": 5,
                # "range_retrofit_fuel": "electricity",
                "replacement_fuel": "propane",
                "resstock_scenarios": [5]
            },
            {
                "range_resstock_scenario": 10,
                "range_retrofit_fuel": "existing",
                "replacement_fuel": "electricity",
                "resstock_scenarios": [10]
            }
        ]

        scenario = 4

        resstock_metadata = {
            "in.cooking_range": "Electric, 100% Usage",
        }

        kwargs = {}

        self.stove = Stove(
            energy_source,
            resstock_consumptions,
            scenario_mapping,
            scenario,
            resstock_metadata,
            **kwargs
        )

    def test_get_energy_consump_baseline(self):
        expected = pd.DataFrame({
            "out.electricity.range_oven.energy_consumption": {
                1: 0, 2: 0, 3: 0, 4: 0
            },
            "out.natural_gas.range_oven.energy_consumption": {
                1: 1, 2: 2, 3: 0, 4: 1
            },
            "out.propane.range_oven.energy_consumption": {
                1: 0, 2: 0, 3: 0, 4: 0
            },
        })

        pd.testing.assert_frame_equal(
            self.stove._get_energy_consump_baseline(),
            expected
        )

    def test_get_retrofit_scenario(self):
        self.assertEqual(
            10,
            self.stove._get_retrofit_scenario()
        )

    def test_get_energy_consump_retrofit(self):
        self.stove._resstock_retrofit_scenario_id = 10

        expected = pd.DataFrame({
            "out.electricity.range_oven.energy_consumption": {
                1: 10, 2: 15, 3: 0, 4: 10
            },
            "out.natural_gas.range_oven.energy_consumption": {
                1: 0, 2: 0, 3: 0, 4: 0
            },
            "out.propane.range_oven.energy_consumption": {
                1: 0, 2: 0, 3: 0, 4: 0
            },
        })

        pd.testing.assert_frame_equal(
            self.stove._get_energy_consump_retrofit(),
            expected
        )

    def test_get_energy_consump_retrofit_npa(self):
        """
        Test the retrofit energy consumption for a NPA retrofit.

        We are most interested when we have an old gas stove converting to propane
        """
        self.stove._resstock_retrofit_scenario_id = 5
        self.stove._scenario = 3

        expected = pd.DataFrame({
            "out.electricity.range_oven.energy_consumption": {
                1: 0, 2: 0, 3: 0, 4: 0
            },
            "out.natural_gas.range_oven.energy_consumption": {
                1: 0, 2: 0, 3: 0, 4: 0
            },
            "out.propane.range_oven.energy_consumption": {
                1: 1, 2: 2, 3: 0, 4: 1
            },
        })

        pd.testing.assert_frame_equal(
            self.stove._get_energy_consump_retrofit(),
            expected
        )


    @unittest.skip
    def test_install_cost(self):
        """
        Test total install cost. Based on inputs, should be:
        (50*2 + (700 + 100) * (1.18) + 50 * 2) * (1.01 ** (2025 - 2020)) = $1202.36
        """
        self.assertListEqual(
            self.stove.get_install_cost(),
            [
                0.0, 0.0, 0.0, 0.0, 0.0, 1202.36, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
            ]
        )
