"""
Contains tests for the Stove end use
"""
import json
import unittest

import pandas as pd

from end_uses.building_end_uses.stove import Stove


class TestStoveIntegration(unittest.TestCase):
    def setUp(self):
        self.energy_source = "natural_gas"
        self.resstock_consumptions = {
            0: pd.DataFrame({
                "out.electricity.range_oven.energy_consumption": {
                    0: 0, 1: 0, 2: 0, 3: 0,
                },
                "out.natural_gas.range_oven.energy_consumption": {
                    0: 0, 1: 1, 2: 2, 3: 1,
                },
                "out.propane.range_oven.energy_consumption": {
                    0: 0, 1: 0, 2: 0, 3: 0,
                }
            }),
            5: pd.DataFrame({
                "out.electricity.range_oven.energy_consumption": {
                    0: 0, 1: 0, 2: 0, 3: 0,
                },
                "out.natural_gas.range_oven.energy_consumption": {
                    0: 0, 1: 1, 2: 2, 3: 1,
                },
                "out.propane.range_oven.energy_consumption": {
                    0: 0, 1: 0, 2: 0, 3: 0,
                }
            }),
            10: pd.DataFrame({
                "out.electricity.range_oven.energy_consumption": {
                    0: 10, 1: 20, 2: 20, 3: 10,
                },
                "out.natural_gas.range_oven.energy_consumption": {
                    0: 0, 1: 0, 2: 0, 3: 0,
                },
                "out.propane.range_oven.energy_consumption": {
                    0: 0, 1: 0, 2: 0, 3: 0,
                }
            }),
        }

        with open("./config_files/scenario_mapping.json") as f:
            data = json.load(f)

        scenario_mapping = data
        scenario = 4
        resstock_metadata = {"in.cooking_range": "Gas, 100% Usage"}
        kwargs = {}

        self.stove = Stove(
            self.energy_source,
            self.resstock_consumptions,
            scenario_mapping,
            scenario,
            resstock_metadata,
            **kwargs
        )

    def test_integration_electrification(self):
        self.stove.initialize_end_use()

        pd.testing.assert_frame_equal(
            self.stove.baseline_energy_use,
            pd.DataFrame({
                "out.electricity.range_oven.energy_consumption": {
                    0: 0, 1: 0, 2: 0, 3: 0,
                },
                "out.natural_gas.range_oven.energy_consumption": {
                    0: 0, 1: 1, 2: 2, 3: 1,
                },
                "out.propane.range_oven.energy_consumption": {
                    0: 0, 1: 0, 2: 0, 3: 0,
                }
            })
        )

        pd.testing.assert_frame_equal(
            self.stove.retrofit_energy_use,
            pd.DataFrame({
                "out.electricity.range_oven.energy_consumption": {
                    0: 10, 1: 20, 2: 20, 3: 10,
                },
                "out.natural_gas.range_oven.energy_consumption": {
                    0: 0, 1: 0, 2: 0, 3: 0,
                },
                "out.propane.range_oven.energy_consumption": {
                    0: 0, 1: 0, 2: 0, 3: 0,
                }
            })
        )

        self.assertEqual(
            self.stove._resstock_retrofit_scenario_id,
            10
        )

    def test_integration_npa(self):
        self.stove._scenario = 3
        self.stove.initialize_end_use()

        pd.testing.assert_frame_equal(
            self.stove.baseline_energy_use,
            pd.DataFrame({
                "out.electricity.range_oven.energy_consumption": {
                    0: 0, 1: 0, 2: 0, 3: 0,
                },
                "out.natural_gas.range_oven.energy_consumption": {
                    0: 0, 1: 1, 2: 2, 3: 1,
                },
                "out.propane.range_oven.energy_consumption": {
                    0: 0, 1: 0, 2: 0, 3: 0,
                }
            })
        )

        pd.testing.assert_frame_equal(
            self.stove.retrofit_energy_use,
            pd.DataFrame({
                "out.electricity.range_oven.energy_consumption": {
                    0: 0, 1: 0, 2: 0, 3: 0,
                },
                "out.natural_gas.range_oven.energy_consumption": {
                    0: 0, 1: 0, 2: 0, 3: 0,
                },
                "out.propane.range_oven.energy_consumption": {
                    0: 0, 1: 1, 2: 2, 3: 1,
                }
            })
        )

        self.assertEqual(
            self.stove._resstock_retrofit_scenario_id,
            5
        )
