"""
Unit tests for the Asset methods
"""
import unittest

import pandas as pd

from end_uses.asset import Asset


class TestAsset(unittest.TestCase):
    def setUp(self):
        install_date = "1/1/2020"
        install_cost = 1000
        lifetime = 10
        sim_start_year = 2020
        sim_end_year = 2040
        replacement_year = 2030

        self.asset = Asset(
            install_date,
            install_cost,
            lifetime,
            sim_start_year,
            sim_end_year,
            replacement_year
        )

        self.asset.initialize_end_use()

    def test_install_year(self):
        self.assertEqual(
            self.asset.install_year,
            2020
        )

    def test_get_years_vector(self):
        self.assertListEqual(
            [2020+i for i in range(20)],
            self.asset.get_years_vector()
        )

    def test_get_year_timestamps(self):
        self.assertListEqual(
            pd.date_range(
                start="2018-01-01", end="2019-01-01", freq="H", inclusive="left"
            ).to_list(),
            self.asset.get_year_timestamps().to_list()
        )

    def test_get_operational_vector(self):
        self.assertListEqual(
            [1] * 10 + [0] * 10,
            self.asset.get_operational_vector()
        )

    def test_get_retrofit_vector(self):
        self.assertListEqual(
            [0] * 10 + [1] * 10,
            self.asset.get_retrofit_vector()
        )

    def test_get_replacement_vec(self):
        self.assertListEqual(
            [False]*10 + [True] + [False]*9,
            self.asset._get_replacement_vec()
        )

    def test_install_cost(self):
        """
        Test install cost vector when install year is during the sim timeframe
        """
        self.assertListEqual(
            [
                1000.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
            ],
            self.asset.get_install_cost()
        )

    def test_install_cost_outter_install(self):
        """
        Test install cost vector when install year is outside the sim timeframe
        """
        self.asset.install_year = 2015

        self.assertListEqual(
            [
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
            ],
            self.asset.get_install_cost()
        )

    def test_fully_depreciate_within(self):
        """
        Test depreciation vec when install and replacement year are fully within the sim timeframe.
        End use fully depreciates (replacement year equals end of lifetime)
        """
        self.asset.install_year = 2025
        self.asset.replacement_year = 2035
        self.asset.initialize_end_use()

        self.assertListEqual(
            [
                0.0, 0.0, 0.0, 0.0, 0.0, 1000.0, 900.0, 800.0, 700.0, 600.0,
                500.0, 400.0, 300.0, 200.0, 100.0, 0.0, 0.0, 0.0, 0.0, 0.0
            ],
            self.asset.get_depreciation()
        )

        self.assertListEqual(
            [
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
            ],
            self.asset.get_stranded_value()
        )

    def test_partial_depreciate_within(self):
        """
        Test depreciation vec when install and replacement year are fully within the sim timeframe.
        End use partially depreciates (replacement year before end of lifetime)
        """
        self.asset.install_year = 2025
        self.asset.replacement_year = 2032
        self.asset.initialize_end_use()

        self.assertListEqual(
            [
                0.0, 0.0, 0.0, 0.0, 0.0, 1000.0, 900.0, 800.0, 700.0, 600.0,
                500.0, 400.0, 300.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
            ],
            self.asset.get_depreciation()
        )

        self.assertListEqual(
            [
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 300.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
            ],
            self.asset.get_stranded_value()
        )

    def test_fully_depreciate_early_install(self):
        """
        Test depreciation vec when install year is before sim start year.
        End use fully depreciates (replacement year equals end of lifetime)
        """
        self.asset.install_year = 2018
        self.asset.replacement_year = 2028
        self.asset.initialize_end_use()

        self.assertListEqual(
            [
                800.0, 700.0, 600.0, 500.0, 400.0, 300.0, 200.0, 100.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
            ],
            self.asset.get_depreciation()
        )

        self.assertListEqual(
            [
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
            ],
            self.asset.get_stranded_value()
        )

    def test_partial_depreciate_early_install(self):
        """
        Test depreciation vec when install year is before sim start year.
        End use partially depreciates (replacement year before end of lifetime)
        """
        self.asset.install_year = 2018
        self.asset.replacement_year = 2025
        self.asset.initialize_end_use()

        self.assertListEqual(
            [
                800.0, 700.0, 600.0, 500.0, 400.0, 300.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
            ],
            self.asset.get_depreciation()
        )

        self.assertListEqual(
            [
                0.0, 0.0, 0.0, 0.0, 0.0, 300.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
            ],
            self.asset.get_stranded_value()
        )

    def test_fully_depreciate_late_replace(self):
        """
        Test depreciation vec when replace year is after sim end year.
        End use fully depreciates (replacement year equals end of lifetime)
        """
        self.asset.install_year = 2035
        self.asset.replacement_year = 2045
        self.asset.initialize_end_use()

        self.assertListEqual(
            [
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 1000.0, 900.0, 800.0, 700.0, 600.0
            ],
            self.asset.get_depreciation()
        )

        self.assertListEqual(
            [
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
            ],
            self.asset.get_stranded_value()
        )

    def test_partial_depreciate_end_year_replace(self):
        """
        Test depreciation vec when replace year is equal to sim end year.
        End use partially depreciates (replacement year before end of lifetime)
        """
        self.asset.install_year = 2030
        self.asset.replacement_year = 2039
        self.asset.initialize_end_use()

        self.assertListEqual(
            [
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                1000.0, 900.0, 800.0, 700.0, 600.0, 500.0, 400.0, 300.0, 200.0, 100.0
            ],
            self.asset.get_depreciation()
        )

        self.assertListEqual(
            [
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 100.0
            ],
            self.asset.get_stranded_value()
        )

    def test_fully_depreciate_end_year_replace(self):
        """
        Test depreciation vec when replace year is equal to sim end year.
        End use fully depreciates (replacement year equals end of lifetime)
        """
        self.asset.install_year = 2029
        self.asset.replacement_year = 2039
        self.asset.initialize_end_use()

        self.assertListEqual(
            [
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1000.0,
                900.0, 800.0, 700.0, 600.0, 500.0, 400.0, 300.0, 200.0, 100.0, 0.0
            ],
            self.asset.get_depreciation()
        )

        self.assertListEqual(
            [
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
            ],
            self.asset.get_stranded_value()
        )

    def test_depreciation_extended_life(self):
        """
        Test the depreciation vector when the asset is replaced after its lifetime (i.e. asset use
        continues after it has fully depreciated)
        """
        self.asset.install_year = 2021
        self.asset.replacement_year = 2035
        self.asset.initialize_end_use()

        self.assertListEqual(
            [
                0.0, 1000.0, 900.0, 800.0, 700.0, 600.0, 500.0, 400.0, 300.0, 200.0,
                100.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 
            ],
            self.asset.get_depreciation()
        )

        self.assertListEqual(
            [
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
            ],
            self.asset.get_stranded_value()
        )

    def test_end_of_life_end_of_sim(self):
        """
        Test when the asset end of life is also the end year of the simulation
        """
        self.asset.replacement_year = 2040
        self.asset.lifetime = 20

        self.asset.initialize_end_use()

        self.assertListEqual(
            [1000 - 50 * i for i in range(20)],
            self.asset.get_depreciation()
        )

        self.assertListEqual(
            [0] * 20,
            self.asset.get_stranded_value()
        )
