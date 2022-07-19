"""
Unit tests for EndUse
"""
import unittest

from end_uses.end_use import EndUse


class TestEndUse(unittest.TestCase):
    def setUp(self):
        install_year = 2020
        end_use_cost = 1000
        lifetime = 15
        elec_consump = 1
        gas_consump = 1
        sim_start_year = 2020
        sim_end_year = 2040
        replacement_year = 2035

        self.end_use = EndUse(
            install_year,
            end_use_cost,
            lifetime,
            elec_consump,
            gas_consump,
            sim_start_year,
            sim_end_year,
            replacement_year
        )

    def test_operational_vec_replace_within(self):
        """
        Test the operational vector when replacement within sim timeframe
        """
        self.assertListEqual(
            [
                1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                1, 1, 1, 1, 1, 0, 0, 0, 0, 0
            ],
            self.end_use.get_operational_vector()
        )

    def test_operational_vec_replace_after(self):
        """
        Test the operational vector when replacement is after the sim timeframe
        """
        self.end_use.install_year = 2030
        self.end_use.replacement_year = 2045

        self.assertListEqual(
            [
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                1, 1, 1, 1, 1, 1, 1, 1, 1, 1
            ],
            self.end_use.get_operational_vector()
        )

    def test_operational_vec_install_prior(self):
        """
        Test the operational vector when end use install is before sim start
        """
        self.end_use.install_year = 2010
        self.end_use.replacement_year = 2022

        self.assertListEqual(
            [
                1, 1, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0
            ],
            self.end_use.get_operational_vector()
        )