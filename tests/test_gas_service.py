"""
Unit tests for GasService class
"""
import unittest
from unittest.mock import Mock

from ttt.end_uses.utility_end_uses.gas_service import GasService


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
            "gas_pipe_intervention_year": 2025,
            "gas_intervention": "decommission",
            "length_ft": 10,
            "pressure": 1,
            "diameter": 1,
            "material": "CI",
            "replacement_cost": 1000,
            "segment_id": "chicago_osage",
            "connected_assets": [self.connected_meter]
        }

        self.gas_service = GasService(**kwargs)
        self.gas_service.years_vector = list(range(2020, 2030))

    def test_get_operational_vector(self):
        """
        Gas service is non-operational after 2025, because the gas service is decommissioned and the
        connected meter is off
        """
        self.assertListEqual(
            [1] * 5 + [0] * 5,
            self.gas_service.get_operational_vector()
        )

    def test_get_replacement_vec(self):
        """
        Gas service is decommissioned in 2025, because the connected meter is turned off
        """
        self.gas_service.operational_vector = [1]*5 + [0]*5
        self.assertListEqual(
            [False]*10,
            self.gas_service._get_replacement_vec()
        )

    def test_replacement_vec_main_replaced_service_off(self):
        """
        The gas main is replaced in 2025, but the gas service is decommissioned because the
        connected meter is turned off
        """
        self.gas_service.operational_vector = [1]*5 + [0]*5
        self.gas_service._gas_shutoff = False
        self.gas_service._gas_replacement = True

        self.assertListEqual(
            [False]*10,
            self.gas_service._get_replacement_vec()
        )

    def test_get_retrofit_vector(self):
        """
        The gas service is not replaced (they system is decommissioned), so always False
        """
        self.gas_service.operational_vector = [1]*5 + [0]*5

        self.assertListEqual(
            [False]*10,
            self.gas_service.get_retrofit_vector()
        )

    def test_retrofit_vec_system_replaced_meter_off(self):
        """
        The gas system is replaced, but always False because the gas meter is off in the replacement
        year
        """
        self.gas_service.operational_vector = [1]*5 + [0]*5
        self.gas_service._gas_shutoff = False
        self.gas_service._gas_replacement = True

        self.assertListEqual(
            [False]*10,
            self.gas_service.get_retrofit_vector()
        )

    def test_retrofit_vec_system_replaced_meter_on(self):
        """
        The gas system is replaced and the service is replaced because the gas meter is on
        """
        self.gas_service.operational_vector = [1]*10
        self.gas_service._gas_shutoff = False
        self.gas_service._gas_replacement = True

        self.assertListEqual(
            [False]*5 + [True]*5,
            self.gas_service.get_retrofit_vector()
        )

    def test_get_install_cost(self):
        """
        Gas service is replaced
        """
        self.gas_service.operational_vector = [1]*10
        self.gas_service._gas_shutoff = False
        self.gas_service._gas_replacement = True

        self.assertListEqual(
            [0.]*5 + [1000.] + [0.]*4,
            self.gas_service.get_install_cost()
        )

    def test_get_depreciation(self):
        """
        Home exits gas system; system decommissioned
        """
        self.gas_service.operational_vector = [1]*5 + [0]*5

        self.assertListEqual(
            [0]*10,
            self.gas_service.get_depreciation()
        )

    def test_get_depreciation_gas_replaced(self):
        """
        Depreciation vector for the service line assuming gas system is replaced and home stays on
        """
        self.gas_service.operational_vector = [1]*10
        self.gas_service._gas_shutoff = False
        self.gas_service._gas_replacement = True

        self.assertListEqual(
            [0.]*5 + [1000. - 25*i for i in range(5)],
            self.gas_service.get_depreciation()
        )

    def test_get_depreciation_early_retirement(self):
        """
        Gas system replaced, but home later exits system
        """
        self.gas_service.operational_vector = [1]*7 + [0]*3
        self.gas_service._gas_shutoff = False
        self.gas_service._gas_replacement = True

        self.assertListEqual(
            [0.]*5 + [1000. - 25*i for i in range(2)] + [0.]*3,
            self.gas_service.get_depreciation()
        )

    def test_get_book_value(self):
        self.gas_service.depreciation = [10, 11, 12]

        self.assertListEqual(
            [10, 11, 12],
            self.gas_service.get_book_value()
        )

    def test_get_shutoff_year(self):
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
        self.gas_service.pipeline_type = "gas_main" # Since we only have mains in the Chicago OM Table

        self.assertListEqual(
            [25000 * (10 / 5280)]*3 + [0]*2,
            self.gas_service._get_annual_om()
        )

        self.gas_service.material = "whatever"
        with self.assertWarns(Warning):
            annual_om = self.gas_service._get_annual_om()

        self.assertListEqual(
            [0]*5,
            annual_om
        )
