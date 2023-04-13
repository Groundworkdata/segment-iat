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

        self.years_vec = [2020, 2021, 2022, 2023, 2024]

        kwargs = {}

        self.stove = Stove(
            energy_source,
            resstock_consumptions,
            scenario_mapping,
            scenario,
            resstock_metadata,
            self.years_vec,
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

    def test_get_existing_book_val(self):
        self.stove._kwargs = {
            "existing_install_year": 2015,
            "lifetime": 10,
            "existing_install_cost": 750,
        }

        expected_book_val = [375., 300., 225., 150., 75.]

        self.assertListEqual(
            expected_book_val,
            self.stove._get_existing_book_val()
        )

    def test_get_replacement_vec(self):
        self.stove._kwargs = {"replacement_year": 2023}

        self.assertListEqual(
            [False, False, False, True, False],
            self.stove._get_replacement_vec()
        )

    def test_get_existing_stranded_val(self):
        self.stove._kwargs = {
            "replacement_year": 2023,
        }

        self.stove.existing_book_val = [500, 400, 300, 200, 100]
        self.stove.replacement_vec = [False, False, False, True, False]

        self.assertListEqual(
            [0, 0, 0, 200, 0],
            self.stove._get_existing_stranded_val()
        )

    def test_get_replacement_cost(self):
        self.stove._kwargs = {
            "replacement_cost": 1000,
            "replacement_year": 2023,
            "escalator": 0.1,
        }

        self.assertListEqual(
            [0, 0, 0, 1100., 0],
            self.stove._get_replacement_cost()
        )

    def test_get_replacement_book_value(self):
        self.stove.replacement_cost = [0, 0, 0, 1200, 0]
        self.stove._kwargs = {
            "replacement_year": 2023,
            "replacement_lifetime": 5,
        }

        self.assertListEqual(
            [0, 0, 0, 1200., 960.,],
            self.stove._get_replacement_book_value()
        )
