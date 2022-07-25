"""
Contains tests for the Stove end use
"""
import unittest

from end_uses.building_end_uses.stove import Stove


class TestStove(unittest.TestCase):
    def setUp(self):
        inputs = {
            "install_year": 2020,
            "asset_cost": 100,
            "replacement_year": 2030,
            "lifetime": 10,
            "sim_start_year": 2020,
            "sim_end_year": 2040,
            "elec_consump": 50,
            "gas_consump": 2000,
            "building_id": "building1",
            "energy_source": "GAS",
            "stove_typ": "GAS",
        }

        self.stove = Stove(**inputs)
        self.stove.initialize_end_use()

    def test_install_cost(self):
        self.assertListEqual(
            self.stove.get_install_cost(),
            [
                1380.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
            ]
        )
