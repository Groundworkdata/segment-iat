"""
Unit tests for the Building module
"""
import json
import unittest
from unittest.mock import Mock

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
            "sim_end_year": 2040
        }

        self.building = Building(
            self.building_params[0],
            self.sim_settings
        )

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
