"""
Unit tests for the GasMeter class
"""
import unittest
from unittest.mock import Mock

from ttt.end_uses.meters.gas_meter import GasMeter


class TestGasMeter(unittest.TestCase):
    def setUp(self):
        building_mock = Mock()
        building_mock.retrofit_scenario = "hybrid_npa"
        building_mock.building_params = {"retrofit_year": 2025}
        building_mock._fuel_type = ["GAS"] * 5 + ["NPH"] * 5

        kwargs = {
            "gisid": "100",
            "parentid": "200",
            "inst_date": "1/1/2010",
            "inst_cost": "2",
            "lifetime": "3",
            "sim_start_year": 2020,
            "sim_end_year": 2030,
            "replacement_year": 2021,
            "decarb_scenario": "hybrid_npa",
            "building": building_mock,
            "gas_shutoff_scenario": True,
            "gas_shutoff_year": 2025
        }

        self.gas_meter = GasMeter(**kwargs)
        self.gas_meter.years_vector = list(range(2020, 2030))

    def test_get_operational_vector(self):
        self.assertListEqual(
            [1] * 5 + [0] * 5,
            self.gas_meter.get_operational_vector()
        )

    def test_get_operational_vector_gas(self):
        self.gas_meter._gas_shutoff = False

        self.assertEqual(
            [1] * 10,
            self.gas_meter.get_operational_vector()
        )

    def test_get_depreciation(self):
        self.assertEqual(
            [0] * 10,
            self.gas_meter.get_depreciation()
        )

    def test_get_retrofit_cost(self):
        self.gas_meter.operational_vector = [1] * 10

        self.assertEqual(
            [0.]*6 + [1000.] + [0.]*3,
            self.gas_meter.get_retrofit_cost()
        )

        self.gas_meter.operational_vector = [1] * 34
        self.gas_meter.years_vector = list(range(2020, 2054))

        self.assertEqual(
            [0.]*6 + [1000.] + [0.]*6 + [1000.] + [0.]*6 + [1000.] + [0.]*6 + [1000.] + [0.]*6,
            self.gas_meter.get_retrofit_cost()
        )
