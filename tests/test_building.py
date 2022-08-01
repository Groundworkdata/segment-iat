"""
Unit tests for the Building module
"""
import unittest
from unittest.mock import Mock

from buildings.building import Building
from end_uses.building_end_uses.stove import Stove


class TestBuilding(unittest.TestCase):
    def setUp(self):
        self.input_filepath = "tests/input_data/building_config.json"
        self.building = Building("Wakefield_01", self.input_filepath)

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

    def test_sum_install_costs(self):
        mock_stove_1 = Mock()
        mock_stove_1.install_cost = [
            100, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        ]

        mock_stove_2 = Mock()
        mock_stove_2.install_cost = [
            0, 0, 0, 0, 0, 0, 70, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        ]

        self.building.end_uses = {
            "stove": {
                "stove1": mock_stove_1,
                "stove2": mock_stove_2
            }
        }

        self.assertListEqual(
            self.building.sum_install_costs(),
            [
                100.0, 0.0, 0.0, 0.0, 0.0, 0.0, 70.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
            ]
        )
