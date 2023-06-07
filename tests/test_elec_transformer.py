""""
Test the ElecTransformer class
"""
import unittest
from unittest.mock import Mock

from end_uses.utility_end_uses.elec_transformer import ElecTransformer


class TestElecTransformer(unittest.TestCase):
    def setUp(self):
        self.kwargs = {
            "gisid": 1,
            "parentid": 2,
            "inst_date": "1/1/1980",
            "inst_cost": 400,
            "lifetime": 40,
            "sim_start_year": 2020,
            "sim_end_year": 2030,
            "replacement_year": 2025,
            "decarb_scenario": "accelerated_elec",
            "circuit": 1,
            "trans_qty": 2,
            "tr_secvolt": 3,
            "PolePadVLT": 4,
            "connected_assets": [],
            "bank_KVA": 100,
        }

        self.elec_transformer = ElecTransformer(**self.kwargs)
        self.elec_transformer.years_vector = list(range(2020, 2030))

    def test_get_annual_bank_kva(self):
        self.assertListEqual(
            [100] * 10,
            self.elec_transformer._get_annual_bank_kva()
        )

    def test_get_upgrade_year(self):
        self.elec_transformer.annual_bank_KVA = [100] * 10
        self.elec_transformer.annual_peak_energy_use = [50*1000] * 5 + [115*1000] * 5

        self.assertEqual(
            2025,
            self.elec_transformer.get_upgrade_year()
        )

        self.assertListEqual(
            [100] * 5 + [200] * 5,
            self.elec_transformer.annual_bank_KVA
        )

    def test_get_upgrade_year_no_upgrade(self):
        self.elec_transformer.annual_bank_KVA = [100] * 10
        self.elec_transformer.annual_peak_energy_use = [50*1000] * 10

        self.assertEqual(
            0,
            self.elec_transformer.get_upgrade_year()
        )

        self.assertListEqual(
            [100] * 10,
            self.elec_transformer.annual_bank_KVA
        )

    def test_update_is_replacement_vector(self):
        self.elec_transformer.required_upgrade_year = 2026

        self.assertListEqual(
            [False]*6 + [True]*4,
            self.elec_transformer.update_is_replacement_vector()
        )

    def test_update_retrofit_vector(self):
        self.elec_transformer.required_upgrade_year = 2027

        self.assertListEqual(
            [False]*7 + [True] + [False]*2,
            self.elec_transformer.update_retrofit_vector()
        )

    def test_get_upgrade_cost(self):
        self.elec_transformer.required_upgrade_year = 2025

        self.assertListEqual(
            [0.]*5 + [2000.] + [0.]*4,
            self.elec_transformer.get_upgrade_cost()
        )

    def test_get_overloading_status(self):
        self.elec_transformer.annual_peak_energy_use = [100, 120, 400, 500, 700, 900]
        self.elec_transformer.annual_bank_KVA = [0.1, 0.95, 0.95, 0.95, 0.95, 0.95]

        self.elec_transformer.get_overloading_status()

        self.assertListEqual(
            [0.] * 6,
            self.elec_transformer.overloading_flag
        )

        self.assertListEqual(
            [1., 12/95, 40/95, 50/95, 70/95, 90/95],
            self.elec_transformer.overloading_ratio
        )
