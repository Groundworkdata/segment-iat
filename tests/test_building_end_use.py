"""
Unit tests for BuildingEndUse
"""
import unittest

from end_uses.building_end_uses.building_end_use import BuildingEndUse


class TestBuildingEndUse(unittest.TestCase):
    def setUp(self):
        install_year = 2020
        end_use_cost = 1000
        lifetime = 15
        sim_start_year = 2020
        sim_end_year = 2040
        replacement_year = 2035

        self.end_use = BuildingEndUse(
            install_year=install_year,
            end_use_cost=end_use_cost,
            lifetime=lifetime,
            elec_consump="./tests/input_data/stoves/elec_stove_elec_consump.json",
            gas_consump="./tests/input_data/stoves/elec_stove_gas_consump.json",
            sim_start_year=sim_start_year,
            sim_end_year=sim_end_year,
            replacement_year=replacement_year
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

    def test_read_elec_consump(self):
        """
        Test that the electrical consumption is read properly
        """
        self.assertDictEqual(
            {
                "2018-01-01T00:00:00": 0.0,
                "2018-01-01T01:00:00": 10.0,
                "2018-01-01T02:00:00": 5.0
            },
            self.end_use.read_elec_consump()
        )

    def test_get_elec_consump(self):
        self.end_use.elec_consump = {
            "2018-01-01T00:00:00": 0.0,
            "2018-01-01T01:00:00": 10.0,
            "2018-01-01T02:00:00": 5.0,
        }

        self.end_use.operational_vector = [0, 0, 1, 1, 1, 0]

        self.assertListEqual(
            [0.0, 0.0, 15.0, 15.0, 15.0, 0.0],
            self.end_use.get_elec_consump()
        )

    def test_get_elec_peak_annual(self):
        self.end_use.elec_consump = {
            "2018-01-01T00:00:00": 0.0,
            "2018-01-01T01:00:00": 10.0,
            "2018-01-01T02:00:00": 5.0,
        }

        self.end_use.operational_vector = [0, 0, 1, 1, 1, 0]

        self.assertListEqual(
            [0.0, 0.0, 10.0, 10.0, 10.0, 0.0],
            self.end_use.get_elec_peak_annual()
        )

    def test_read_gas_consump(self):
        """
        Test that the electrical consumption is read properly
        """
        self.assertDictEqual(
            {
                "2018-01-01T00:00:00": 50.0,
                "2018-01-01T01:00:00": 0.0,
                "2018-01-01T02:00:00": 45.0
            },
            self.end_use.read_gas_consump()
        )

    def test_get_gas_consump(self):
        self.end_use.gas_consump = {
            "2018-01-01T00:00:00": 30.0,
            "2018-01-01T01:00:00": 10.0,
            "2018-01-01T02:00:00": 5.0,
        }

        self.end_use.operational_vector = [0, 0, 1, 1, 1, 1]

        self.assertListEqual(
            [0.0, 0.0, 45.0, 45.0, 45.0, 45.0],
            self.end_use.get_gas_consump()
        )

    def test_get_gas_peak_annual(self):
        self.end_use.gas_consump = {
            "2018-01-01T00:00:00": 30.0,
            "2018-01-01T01:00:00": 10.0,
            "2018-01-01T02:00:00": 5.0,
        }

        self.end_use.operational_vector = [0, 0, 1, 1, 1, 1]

        self.assertListEqual(
            [0.0, 0.0, 30.0, 30.0, 30.0, 30.0],
            self.end_use.get_gas_peak_annual()
        )
