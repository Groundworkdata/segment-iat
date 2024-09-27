"""
Defines a thermal energy network class
"""
from typing import Any, Dict, List

import pandas as pd

from segment_iat.buildings.building import Building


DEFAULT_TEN_ID = "TEN_1"
DEFAULT_LIFETIME = 50
KW_TO_TONS = 3.412 / 12 # (3.412 kBTU/hr / kW) * (1 ton / 12 kBTU/hr)


class ThermalEnergyNetwork:
    """
    Thermal Energy Network class

    Args:
        years_vec (List[int]): List of simulation years
        year_timestamps (pd.DatetimeIndex): Index for timeseries data
        buildings (Dict[str, Building]): Dict of Building classes, organized by ID
        ten_config (Dict[str, Any]): Dict of TEN configuration values
        {
            asset_id (str): The ID of the TEN
            install_cost_per_ton (float): Capital installation cost of TEN in $ / ton of capacity
            lifetime (int): Useful life of the TEN in years
            om_per_cust (float): O&M cost of the TEN in $ / customer
        }

    Attributes:
        asset_id (str): ID for the TEN
        install_year (int): The installation year of the TEN
        operational_vector (List[int]): 1 for years when TEN is in operation, 0 o/w
        annual_load_heating (List[float]): The total annual heating load for the TEN, in kBTU
        annual_load_cooling (List[float]): The total annual cooling load for the TEN, in kBTU
        annual_load_total (List[float]): Sum of annual_heating_load and annual_cooling_load
        annual_peak_heating (List[float]): The total annual peak heating demand, in kBTU/hr
        annual_peak_cooling (List[float]): The total annual peak cooling demand, in kBTU/hr
        annual_peak_network (List[float]): The max of annual_heating_peak and annual_cooling_peak
        install_cost (float): The total capital cost to install the TEN
        install_cost_vec (List[float]): Equals the install cost in the install year, 0 o/w
        lifetime (int): The TEN lifetime in years
        book_value_vec (List[float]): Annual book value of the TEN. Assumes straight-line depreciation
        annual_customers (List[int]): Number of connected customers each year
        annual_om_vec (List[float]): Annual O&M cost of the TEN

    Methods:
        create_network (None): Calculates network attributes
    """
    def __init__(
            self,
            years_vec: List[int],
            year_timestamps: pd.DatetimeIndex,
            buildings: Dict[str, Building],
            ten_config: Dict[str, Any]
    ):
        self._years_vec: List[int] = years_vec
        self._year_timestamps: pd.DatetimeIndex = year_timestamps
        self._buildings: Dict[str, Building] = buildings
        self._ten_config: Dict[str, Any] = ten_config

        self.asset_id: str = ""

        self.install_year: int = 0
        self.operational_vector: List[int] = []

        self.annual_load_heating: List[float] = []
        self.annual_load_cooling: List[float] = []
        self.annual_load_total: List[float] = []
        self.annual_peak_heating: List[float] = []
        self.annual_peak_cooling: List[float] = []
        self.annual_peak_network: List[float] = []

        self.install_cost: float = 0
        self.install_cost_vec: List[float] = []
        self.lifetime: int = 0
        self.book_value_vec: List[float] = []
        self.annual_customers: List[int] = []
        self.annual_om_vec: List[float] = []

    def create_network(self) -> None:
        """
        Calculate network attributes
        """
        self.asset_id = self._ten_config.get("asset_id", DEFAULT_TEN_ID)

        #TODO: Expand QA using some of these attributes
        self.install_year = int(self._ten_config.get("install_year", self._years_vec[0]))
        self.operational_vector = self._get_operational_vector()

        self.annual_load_heating = self._calc_annual_load("heating")
        self.annual_load_cooling = self._calc_annual_load("cooling")
        self.annual_load_total = self._calc_annual_load_total()
        self.annual_peak_heating = self._calc_annual_peak("heating")
        self.annual_peak_cooling = self._calc_annual_peak("cooling")

        self.install_cost = self._get_install_cost()
        self.install_cost_vec = self._get_install_cost_vec()
        self.lifetime = int(self._ten_config.get("lifetime", DEFAULT_LIFETIME))
        self.book_value_vec = self._get_book_value_vec()
        self.annual_customers = self._get_annual_customers()
        self.annual_om_vec = self._get_annual_om_vec()

    def _get_operational_vector(self) -> List[int]:
        """
        Get the operational vector of the TEN, over the Study timeframe
        """
        return [
            1 if self.install_year >= i else 0
            for i in self._years_vec
        ]

    def _calc_annual_load(self, heating_cooling: str) -> List[float]:
        """
        Calculate the annual load (heating or cooling) for the TEN based on connected buildings

        Args:
            heating_cooling (str): Str indicating if calculating total heating or cooling load;
                allowable values of 'heating' or 'cooling'

        Returns:
            list: Annual thermal load (heating or cooling) for each year in the Study
        """
        annual_load = {}

        for bldg_id, bldg in self._buildings.items():
            annual_ten_load = bldg.annual_energy_by_fuel.get(f"thermal_{heating_cooling}")
            annual_load[bldg_id] = annual_ten_load

        annual_load = pd.DataFrame(annual_load, index=self._years_vec)
        return annual_load.sum(axis=1).to_list()

    def _calc_annual_load_total(self) -> List[float]:
        """
        Calculate the total annual load as the suem of annual heating and cooling load

        Args:
            None

        Returns:
            list: Annual thermal load (heating + cooling) for each year in the Study
        """
        thermal_load = pd.DataFrame({
            "heating": self._calc_annual_load("heating"),
            "cooling": self._calc_annual_load("cooling")
        }).sum(axis=1).to_list()

        return thermal_load

    def _calc_annual_peak(self, heating_cooling: str) -> List[float]:
        """
        Calculate the peak thermal load (heating or cooling) each year for the TEN

        Args:
            heating_cooling (str): Str indicating if calculating total heating or cooling load;
                allowable values of 'heating' or 'cooling'

        Returns:
            list: Annual peak thermal load (heating or cooling) for each year in the Study
        """
        annual_peak = []

        #FIXME: Ugly code
        for i, _ in enumerate(self._years_vec):
            total_thermal_consump = pd.Series(0, index=self._year_timestamps)

            for bldg in self._buildings.values():
                if bldg._is_retrofit_vec[i]:
                    total_thermal_consump = total_thermal_consump.add(
                        bldg.retrofit_consumption[
                            f"out.thermal_{heating_cooling}.total.energy_consumption"
                        ]
                    )
                else:
                    total_thermal_consump = total_thermal_consump.add(
                        bldg.baseline_consumption[
                            f"out.thermal_{heating_cooling}.total.energy_consumption"
                        ]
                    )

            annual_peak.append(total_thermal_consump.max())

        return annual_peak

    def _calc_annual_peak_network(self) -> List[float]:
        """
        Calculate the peak demand of the TEN each year; the max of heating and cooling peaks

        Args:
            None

        Returns:
            list: Annual peak thermal load for each year in the Study
        """
        annual_peaks = pd.DataFrame(
            {"heating": self.annual_peak_heating, "cooling": self.annual_peak_cooling},
            index=self._years_vec
        )

        return annual_peaks.max(axis=1).to_list()

    def _get_install_cost(self) -> float:
        """
        This first pass assumes install cost is based on calculated annual peak of the network
        """
        cost_rate = float(self._ten_config.get("install_cost_per_ton", 0))
        network_peak = self._calc_annual_peak_network()
        max_peak = max(network_peak) # in kW
        max_peak = max_peak * KW_TO_TONS # tons
        return cost_rate * max_peak

    def _get_install_cost_vec(self) -> List[float]:
        """
        Install cost as a vector over the Study years
        """
        return [
            self.install_cost if i==self.install_year
            else 0
            for i in self._years_vec
        ]

    def _get_book_value_vec(self) -> List[float]:
        """
        Book value over the Study years. Assumes straight-line depreciation over the TEN lifetime
        """
        annual_depreciation = self.install_cost / self.lifetime

        book_value = [
            max(self.install_cost - (annual_depreciation * (i - self.install_year)), 0)
            if i >= self.install_year
            else 0
            for i in self._years_vec
        ]

        return book_value

    def _get_annual_customers(self) -> List[float]:
        """
        Get number of customers each year
        """
        bldg_fuels = pd.DataFrame(
            {bldg_id: bldg._fuel_type for bldg_id, bldg in self._buildings.items()},
            index=self._years_vec
        )

        num_custs = bldg_fuels.apply(lambda x: sum([1 if y=="TEN" else 0 for y in x]), axis=1)
        return num_custs.to_list()

    def _get_annual_om_vec(self) -> List[float]:
        """
        Assumes a constant O&M rate per connected building
        """
        om_rate = float(self._ten_config.get("om_per_cust", 0))
        return [
            om_rate * i
            for i in self.annual_customers
        ]
