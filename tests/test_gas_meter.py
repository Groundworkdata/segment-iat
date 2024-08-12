"""
Unit tests for the GasMeter class
"""
import unittest
from unittest.mock import Mock

from segment_iat.end_uses.meters.gas_meter import GasMeter


class TestGasMeter(unittest.TestCase):
    def setUp(self):
        self.building_mock = Mock()
        self.building_mock.building_params = {"retrofit_year": 2025}
        self.building_mock._fuel_type = ["GAS"] * 5 + ["NPH"] * 5

        kwargs = {
            "gisid": "100",
            "parentid": "200",
            "inst_date": "1/1/2010",
            "inst_cost": "2",
            "lifetime": "3",
            "sim_start_year": 2020,
            "sim_end_year": 2030,
            "replacement_year": 2021,
            "building": self.building_mock,
            "gas_pipe_intervention_year": 2025,
            "gas_intervention": "decommission"
        }

        self.gas_meter = GasMeter(**kwargs)
        self.gas_meter.years_vector = list(range(2020, 2030))

    def test_get_operational_vector(self):
        """
        Home gets off gas in 2025; pipe segment is decommissioned
        """
        self.assertListEqual(
            [1] * 5 + [0] * 5,
            self.gas_meter.get_operational_vector()
        )

    def test_get_operational_vector_replace(self):
        """
        Home gets off gas in 2025; pipe segment is replaced
        """
        self.gas_meter._gas_shutoff = False

        self.assertListEqual(
            [1] * 5 + [0] * 5,
            self.gas_meter.get_operational_vector()
        )

    def test_get_operational_vector_home_on(self):
        """
        Gas pipe is replaced and home stays on gas
        """
        self.gas_meter.building._fuel_type = ["GAS"] * 10
        self.gas_meter._gas_intervention = "replace"
        self.gas_meter._gas_shutoff = False

        self.assertListEqual(
            [1] * 10,
            self.gas_meter.get_operational_vector()
        )

    def test_home_off_year1(self):
        """
        Home gets off gas in the first year
        """
        self.gas_meter.building._fuel_type = ["NPH"] * 10
        self.gas_meter._gas_intervention = "replace"
        self.gas_meter._gas_shutoff = False

        self.assertListEqual(
            [0] * 10,
            self.gas_meter.get_operational_vector()
        )

    def test_get_depreciation(self):
        self.assertEqual(
            [0] * 10,
            self.gas_meter.get_depreciation()
        )

    def test_get_retrofit_cost(self):
        """
        Gas meter is in use for the entire sim and replaced at the default frequency (7 years)
        """
        self.gas_meter.operational_vector = [1] * 10

        self.assertEqual(
            [0.]*6 + [1000.] + [0.]*3,
            self.gas_meter.get_retrofit_cost()
        )

        self.gas_meter.operational_vector = [1] * 34
        self.gas_meter.years_vector = list(range(2020, 2054))

        self.assertEqual(
            [0.]*6 + [1000.] + [0.]*6 + [1000.] + [0.]*6 + [1000.] + [0.]*6 + [1000.] + [0.]*6,
            self.gas_meter.get_retrofit_cost()
        )

    def test_get_retrofit_cost_no_freq(self):
        """
        Gas meter in use for entire sim and only replaced once (gas system is replaced in 2025)
        """
        self.gas_meter.operational_vector = [1] * 10
        self.gas_meter._retrofit_freq = 0
        self.gas_meter.operational_vector = [1] * 34
        self.gas_meter.years_vector = list(range(2020, 2054))
        self.gas_meter._gas_shutoff = False

        self.assertEqual(
            [0.]*5 + [1000.] + [0.]*28,
            self.gas_meter.get_retrofit_cost()
        )
