"""
Contains tests for the Stove end use
"""
import json
import unittest

import pandas as pd

from ttt.end_uses.building_end_uses.stove import Stove


class TestStoveIntegration(unittest.TestCase):
    def setUp(self):
        self.energy_source = "natural_gas"
        self.resstock_consumptions = {}

        self.custom_baseline_consump = pd.DataFrame({
            "out.electricity.range_oven.energy_consumption": {0: 0, 1: 0, 2: 1, 3: 0},
            "out.electricity.other.energy_consumption": {0: 0, 1: 0, 2: 1, 3: 1000},
        })

        self.custom_retrofit_consump = pd.DataFrame({
            "out.electricity.range_oven.energy_consumption": {0: 0, 1: 0, 2: 12, 3: 0},
            "out.electricity.other.energy_consumption": {0: 0, 1: 5, 2: 1, 3: 1000},
        })

        scenario = 4
        years_vec = [0, 1, 2, 3]

        kwargs = {
            "replacement_year": 3,
            "existing_install_year": 0,
            "lifetime": 10,
            "existing_install_cost": 5,
            "replacement_cost": 6,
            "replacement_cost_dollars_year": 0,
            "replacement_lifetime": 10,
        }

        self.stove = Stove(
            years_vec,
            custom_baseline_energy=self.custom_baseline_consump,
            custom_retrofit_energy=self.custom_retrofit_consump,
            **kwargs
        )

    def test_integration_electrification(self):
        self.stove.initialize_end_use()

        pd.testing.assert_frame_equal(
            self.stove.baseline_energy_use,
            pd.DataFrame({
                "out.electricity.range_oven.energy_consumption": {0: 0, 1: 0, 2: 1, 3: 0},
                "out.natural_gas.range_oven.energy_consumption": {0: 0, 1: 0, 2: 0, 3: 0},
                "out.propane.range_oven.energy_consumption": {0: 0, 1: 0, 2: 0, 3: 0},
            })
        )

        pd.testing.assert_frame_equal(
            self.stove.retrofit_energy_use,
            pd.DataFrame({
                "out.electricity.range_oven.energy_consumption": {0: 0, 1: 0, 2: 12, 3: 0},
                "out.natural_gas.range_oven.energy_consumption": {0: 0, 1: 0, 2: 0, 3: 0},
                "out.propane.range_oven.energy_consumption": {0: 0, 1: 0, 2: 0, 3: 0},
            })
        )
