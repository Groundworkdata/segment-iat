"""
Contains tests for the Stove end use
"""
import unittest

import pandas as pd

from segment_iat.end_uses.building_end_uses.stove import Stove


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

        self.years_vec = [2020, 2021, 2022, 2023, 2024]

        kwargs = {}

        self.stove = Stove(
            self.years_vec,
            **kwargs
        )

    def test_get_custom_energies(self):
        self.stove._custom_baseline_energy = pd.DataFrame({
            "out.natural_gas.range_oven.energy_consumption": {0: 10, 1: 3},
            "out.electricity.something": {0: 0, 1: 10},
        })

        self.stove._custom_retrofit_energy = pd.DataFrame({
            "out.electricity.range_oven.energy_consumption": {0: 10, 1: 3},
            "out.electricity.something_else": {0: 0, 1: 10},
        })

        self.stove._get_custom_energies()

        pd.testing.assert_frame_equal(
            self.stove.baseline_energy_use,
            pd.DataFrame({
                "out.electricity.range_oven.energy_consumption": {0: 0, 1: 0},
                "out.natural_gas.range_oven.energy_consumption": {0: 10, 1: 3},
                "out.propane.range_oven.energy_consumption": {0: 0, 1: 0},
            })
        )

        pd.testing.assert_frame_equal(
            self.stove.retrofit_energy_use,
            pd.DataFrame({
                "out.electricity.range_oven.energy_consumption": {0: 10, 1: 3},
                "out.natural_gas.range_oven.energy_consumption": {0: 0, 1: 0},
                "out.propane.range_oven.energy_consumption": {0: 0, 1: 0},
            })
        )

    def test_get_existing_book_val(self):
        self.stove._kwargs = {
            "existing_install_year": 2015,
            "lifetime": 10,
            "existing_install_cost": 750,
            "escalator": 0,
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
        self.stove._replacement_vec = [False, False, False, True, False]

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
