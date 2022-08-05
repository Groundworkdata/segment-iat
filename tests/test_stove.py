"""
Contains tests for the Stove end use
"""
import unittest

from end_uses.building_end_uses.stove import Stove


class TestStove(unittest.TestCase):
    def setUp(self):
        inputs = {
            "install_year": 2025,
            "asset_cost": 700,
            "replacement_year": 2030,
            "lifetime": 10,
            "sim_start_year": 2020,
            "sim_end_year": 2040,
            "elec_consump": 50,
            "gas_consump": 2000,
            "building_id": "building1",
            "energy_source": "GAS",
            "stove_typ": "GAS",
            "removal_labor_time": 2,
            "labor_rate": 50,
            "misc_supplies_price": 100,
            "retail_markup": 0.18,
            "installation_labor_time": 2,
            "annual_cost_escalation": 0.01
        }

        self.stove = Stove(**inputs)
        self.stove.initialize_end_use()

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
