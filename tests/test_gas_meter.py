"""
Unit tests for the GasMeter class
"""
import unittest
from unittest.mock import Mock

from end_uses.meters.gas_meter import GasMeter


class TestGasMeter(unittest.TestCase):
    def setUp(self):
        building_mock = Mock()
        building_mock.retrofit_scenario = "hybrid_npa"
        building_mock.building_params = {"retrofit_year": 2025}

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
        }

        self.gas_meter = GasMeter(**kwargs)

    def test_get_operational_vector(self):
        self.gas_meter.years_vector = list(range(2020, 2030))

        self.assertListEqual(
            [1] * 5 + [0] * 5,
            self.gas_meter.get_operational_vector()
        )

    def test_get_operational_vector_gas(self):
        self.gas_meter.years_vector = list(range(2020, 2030))
        self.gas_meter.building.retrofit_scenario = "hybrid_gas"

        self.assertEqual(
            [1] * 10,
            self.gas_meter.get_operational_vector()
        )
