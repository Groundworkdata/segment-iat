"""
Integration tests for the gas service line
"""
import unittest
from unittest.mock import Mock

from ttt.end_uses.utility_end_uses.gas_service import GasService


class TestGasService(unittest.TestCase):
    def setUp(self):
        self.connected_meter = Mock()
        self.connected_meter.annual_total_energy_use = {
            **{i: 30 for i in range(2020, 2025)},
            **{i: 0 for i in range(2025, 2030)}
        }
        self.connected_meter.annual_peak_energy_use = {
            **{i: 45 for i in range(2020, 2025)},
            **{i: 0 for i in range(2025, 2030)}
        }
        self.connected_meter.operational_vector = [1]*5 + [0]*5
        self.connected_meter.building._retrofit_vec = [0]*5 + [1] + [0]*4

        kwargs = {
            "gisid": "1",
            "parentid": "2",
            "inst_date": "1/1/1980",
            "inst_cost": 1000,
            "lifetime": 40,
            "sim_start_year": 2020,
            "sim_end_year": 2030,
            "replacement_year": 2060,
            "decarb_scenario": "hybrid_npa",
            "length_ft": 10,
            "pressure": 1,
            "diameter": 1,
            "material": "WS",
            "replacement_cost": 1000,
            "connected_assets": [self.connected_meter]
        }

        self.gas_service = GasService(**kwargs)
        self.gas_service.initialize_end_use()

    def test_annual_total_leaks(self):
        self.assertListEqual(
            [0.227*10]*5 + [0]*5,
            self.gas_service.annual_total_leakage
        )

    def test_annual_total_energy_use(self):
        self.assertDictEqual(
            {
                2020: 30, 2021: 30, 2022: 30, 2023: 30, 2024: 30,
                2025: 0, 2026: 0, 2027: 0, 2028: 0, 2029: 0
            },
            self.gas_service.annual_total_energy_use
        )

    def test_annual_peak_energy_use(self):
        self.assertDictEqual(
            {
                2020: 45, 2021: 45, 2022: 45, 2023: 45, 2024: 45,
                2025: 0, 2026: 0, 2027: 0, 2028: 0, 2029: 0
            },
            self.gas_service.annual_peak_energy_use
        )

    def test_stranded_value(self):
        self.assertListEqual(
            [
                0, 0, 0, 0, 0,
                0, 0, 0, 0, 0
            ],
            self.gas_service.stranded_value
        )
