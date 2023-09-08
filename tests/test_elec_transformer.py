""""
Test the ElecTransformer class
"""
import unittest
from unittest.mock import Mock

from ttt.end_uses.utility_end_uses.elec_transformer import ElecTransformer


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
        self.elec_transformer.annual_peak_energy_use = [50] * 5 + [130] * 5

        self.assertListEqual(
            [2025],
            self.elec_transformer.get_upgrade_year()
        )

        self.assertListEqual(
            [100] * 5 + [200] * 5,
            self.elec_transformer.annual_bank_KVA
        )

        self.assertListEqual(
            [0]*5 + [1] + [0]*4,
            self.elec_transformer.annual_upgrades
        )

    def test_get_upgrade_year_no_upgrade(self):
        self.elec_transformer.annual_bank_KVA = [100] * 10
        self.elec_transformer.annual_peak_energy_use = [50] * 10

        self.assertEqual(
            [],
            self.elec_transformer.get_upgrade_year()
        )

        self.assertListEqual(
            [100] * 10,
            self.elec_transformer.annual_bank_KVA
        )

        self.assertListEqual(
            [0]*10,
            self.elec_transformer.annual_upgrades
        )

    def test_update_is_replacement_vector(self):
        self.elec_transformer.required_upgrade_year = [2026]

        self.assertListEqual(
            [False]*6 + [True]*4,
            self.elec_transformer.update_is_replacement_vector()
        )

    def test_update_retrofit_vector(self):
        self.elec_transformer.required_upgrade_year = [2027]

        self.assertListEqual(
            [False]*7 + [True] + [False]*2,
            self.elec_transformer.update_retrofit_vector()
        )

    def test_get_upgrade_cost(self):
        self.elec_transformer.annual_upgrades = [0]*5 + [1] +[0]*4

        self.assertListEqual(
            [0.]*5 + [20000.] + [0.]*4,
            self.elec_transformer.get_upgrade_cost()
        )

    def test_get_overloading_status(self):
        self.elec_transformer.annual_peak_energy_use = [100, 120, 400, 510, 700, 900]
        self.elec_transformer.annual_bank_KVA = [200, 200, 200, 400, 400, 400]

        self.elec_transformer.get_overloading_status()

        self.assertListEqual(
            [0.]*2 + [1.]*4,
            self.elec_transformer.overloading_flag
        )

        self.assertListEqual(
            [1/(2*1.25), 12/(20*1.25), 2/1.25, 51/(40*1.25), 70/(40*1.25), 90/(40*1.25)],
            self.elec_transformer.overloading_ratio
        )
