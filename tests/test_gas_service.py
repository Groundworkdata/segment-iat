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
        self.connected_meter.building._retrofit_vec = [0, 0, 0, 0, 1, 0, 0, 0, 0, 0]

        kwargs = {
            "gisid": "1",
            "parentid": "2",
            "inst_date": "1/1/1980",
            "inst_cost": 500,
            "lifetime": 40,
            "sim_start_year": 2020,
            "sim_end_year": 2030,
            "replacement_year": 2060,
            "decarb_scenario": "hybrid_gas",
            "length_ft": 10,
            "pressure": 1,
            "diameter": 1,
            "material": "WS",
            "replacement_cost": 1000,
            "connected_assets": [self.connected_meter]
        }

        self.gas_service = GasService(**kwargs)
        self.gas_service.years_vector = list(range(2020, 2030))

    def test_get_operational_vector(self):
        self.assertListEqual(
            [1] * 5 + [0] * 5,
            self.gas_service.get_operational_vector()
        )

    def test_get_replacement_vec(self):
        self.assertListEqual(
            [False]*5 + [True] + [False]*4,
            self.gas_service._get_replacement_vec()
        )

    def test_get_replacement_vec_no_replace(self):
        self.gas_service.decarb_scenario = "hybrid_npa"

        self.assertListEqual(
            [False]*10,
            self.gas_service._get_replacement_vec()
        )

    def test_get_retrofit_vector(self):
        self.assertListEqual(
            [False]*5 + [True]*5,
            self.gas_service.get_retrofit_vector()
        )

        self.gas_service.decarb_scenario = "hybrid_npa"

        self.assertListEqual(
            [False]*10,
            self.gas_service.get_retrofit_vector()
        )

    def test_get_install_cost(self):
        self.assertListEqual(
            [0.]*5 + [1000.] + [0.]*4,
            self.gas_service.get_install_cost()
        )

    def test_get_depreciation(self):
        self.assertListEqual(
            [0.]*5 + [1000. - 25*i for i in range(5)],
            self.gas_service.get_depreciation()
        )

    def test_get_book_value(self):
        self.gas_service.depreciation = [10, 11, 12]

        self.assertListEqual(
            [10, 11, 12],
            self.gas_service.get_book_value()
        )

    def test_get_shutoff_year(self):
        self.gas_service.decarb_scenario = "hybrid_npa"

        self.assertListEqual(
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            self.gas_service.get_shutoff_year()
        )

    def test_update_stranded_value(self):
        self.gas_service.book_value = [1, 1, 2]
        self.gas_service.shutoff_year = [0, 1, 0]

        self.assertListEqual(
            [0, 1, 0],
            self.gas_service._update_stranded_value()
        )

    def test_get_annual_om(self):
        self.gas_service.operational_vector = [1, 1, 1, 0, 0]

        self.assertListEqual(
            [7500 * (10 / 5280)]*3 + [0]*2,
            self.gas_service._get_annual_om()
        )

        self.gas_service.material = "whatever"
        with self.assertWarns(Warning):
            annual_om = self.gas_service._get_annual_om()

        self.assertListEqual(
            [0]*5,
            annual_om
        )
