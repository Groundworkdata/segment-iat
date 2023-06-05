"""
Unit tests for GasService class
"""
import unittest
from unittest.mock import Mock

from end_uses.utility_end_uses.gas_service import GasService


class TestGasService(unittest.TestCase):
    def setUp(self):
        self.connected_meter = Mock()
        self.connected_meter.operational_vector = [1] * 5 + [0] * 5

        kwargs = {
            "gisid": "1",
            "parentid": "2",
            "inst_date": "1/1/1980",
            "inst_cost": 1000,
            "lifetime": 80,
            "sim_start_year": 2020,
            "sim_end_year": 2030,
            "replacement_year": 2060,
            "decarb_scenario": "hybrid_npa",
            "length_ft": 10,
            "pressure": 1,
            "diameter": 1,
            "material": "WC",
            "connected_assets": [self.connected_meter]
        }

        self.gas_service = GasService(**kwargs)

    def test_get_operational_vector(self):
        self.gas_service.years_vector = list(range(2020, 2030))

        self.assertListEqual(
            [1] * 5 + [0] * 5,
            self.gas_service.get_operational_vector()
        )

    def test_get_replacement_vec(self):
        self.gas_service.years_vector = list(range(2020, 2030))

        self.assertListEqual(
            [False]*5 + [True] + [False]*4,
            self.gas_service._get_replacement_vec()
        )

    def test_get_replacement_vec_no_replace(self):
        self.gas_service.years_vector = list(range(2020, 2030))
        self.connected_meter.operational_vector = [1]*10

        self.assertListEqual(
            [False]*10,
            self.gas_service._get_replacement_vec()
        )

    def test_get_replacement_vec_multiple_assets(self):
        self.gas_service.years_vector = list(range(2020, 2030))

        second_asset = Mock()
        second_asset.operational_vector = [1]*7 + [0]*3
        self.gas_service.connected_assets.append(second_asset)

        self.assertListEqual(
            [False]*7 + [True] + [False]*2,
            self.gas_service._get_replacement_vec()
        )
