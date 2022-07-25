"""
Unit tests for the Asset methods
"""
import unittest

from end_uses.asset import Asset


class TestAsset(unittest.TestCase):
    def setUp(self):
        install_year = 2020
        install_cost = 1000
        lifetime = 10
        sim_start_year = 2020
        sim_end_year = 2040
        replacement_year = 2030

        self.stove = Asset(
            install_year,
            install_cost,
            replacement_year,
            lifetime,
            sim_start_year,
            sim_end_year
        )

        self.stove.initialize_end_use()

    def test_fully_depreciate_within(self):
        """
        Test depreciation vec when install and replacement year are fully within the sim timeframe.
        End use fully depreciates (replacement year equals end of lifetime)
        """
        self.stove.install_year = 2025
        self.stove.replacement_year = 2035
        self.stove.initialize_end_use()

        self.assertListEqual(
            [
                0.0, 0.0, 0.0, 0.0, 0.0, 1000.0, 900.0, 800.0, 700.0, 600.0,
                500.0, 400.0, 300.0, 200.0, 100.0, 0.0, 0.0, 0.0, 0.0, 0.0
            ],
            self.stove.get_depreciation()
        )

        self.assertListEqual(
            [
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
            ],
            self.stove.get_stranded_value()
        )

    def test_partial_depreciate_within(self):
        """
        Test depreciation vec when install and replacement year are fully within the sim timeframe.
        End use partially depreciates (replacement year before end of lifetime)
        """
        self.stove.install_year = 2025
        self.stove.replacement_year = 2032
        self.stove.initialize_end_use()

        self.assertListEqual(
            [
                0.0, 0.0, 0.0, 0.0, 0.0, 1000.0, 900.0, 800.0, 700.0, 600.0,
                500.0, 400.0, 300.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
            ],
            self.stove.get_depreciation()
        )

        self.assertListEqual(
            [
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 300.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
            ],
            self.stove.get_stranded_value()
        )

    def test_fully_depreciate_early_install(self):
        """
        Test depreciation vec when install year is before sim start year.
        End use fully depreciates (replacement year equals end of lifetime)
        """
        self.stove.install_year = 2018
        self.stove.replacement_year = 2028
        self.stove.initialize_end_use()

        self.assertListEqual(
            [
                800.0, 700.0, 600.0, 500.0, 400.0, 300.0, 200.0, 100.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
            ],
            self.stove.get_depreciation()
        )

        self.assertListEqual(
            [
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
            ],
            self.stove.get_stranded_value()
        )

    def test_partial_depreciate_early_install(self):
        """
        Test depreciation vec when install year is before sim start year.
        End use partially depreciates (replacement year before end of lifetime)
        """
        self.stove.install_year = 2018
        self.stove.replacement_year = 2025
        self.stove.initialize_end_use()

        self.assertListEqual(
            [
                800.0, 700.0, 600.0, 500.0, 400.0, 300.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
            ],
            self.stove.get_depreciation()
        )

        self.assertListEqual(
            [
                0.0, 0.0, 0.0, 0.0, 0.0, 300.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
            ],
            self.stove.get_stranded_value()
        )

    def test_fully_depreciate_late_replace(self):
        """
        Test depreciation vec when replace year is after sim end year.
        End use fully depreciates (replacement year equals end of lifetime)
        """
        self.stove.install_year = 2035
        self.stove.replacement_year = 2045
        self.stove.initialize_end_use()

        self.assertListEqual(
            [
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 1000.0, 900.0, 800.0, 700.0, 600.0
            ],
            self.stove.get_depreciation()
        )

        self.assertListEqual(
            [
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
            ],
            self.stove.get_stranded_value()
        )

    def test_partial_depreciate_end_year_replace(self):
        """
        Test depreciation vec when replace year is equal to sim end year.
        End use partially depreciates (replacement year before end of lifetime)
        """
        self.stove.install_year = 2030
        self.stove.replacement_year = 2039
        self.stove.initialize_end_use()

        self.assertListEqual(
            [
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                1000.0, 900.0, 800.0, 700.0, 600.0, 500.0, 400.0, 300.0, 200.0, 100.0
            ],
            self.stove.get_depreciation()
        )

        self.assertListEqual(
            [
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 100.0
            ],
            self.stove.get_stranded_value()
        )

    def test_fully_depreciate_end_year_replace(self):
        """
        Test depreciation vec when replace year is equal to sim end year.
        End use fully depreciates (replacement year equals end of lifetime)
        """
        self.stove.install_year = 2029
        self.stove.replacement_year = 2039
        self.stove.initialize_end_use()

        self.assertListEqual(
            [
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1000.0,
                900.0, 800.0, 700.0, 600.0, 500.0, 400.0, 300.0, 200.0, 100.0, 0.0
            ],
            self.stove.get_depreciation()
        )

        self.assertListEqual(
            [
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
            ],
            self.stove.get_stranded_value()
        )
