"""
Defines a thermal energy network class
"""
from typing import Dict

import pandas as pd

from segment_iat.buildings.building import Building


DEFAULT_TEN_ID = "TEN_1"


class ThermalEnergyNetwork:
    """
    Thermal Energy Network class

    Args:
        years_vec (list): List of simulation years
        year_timestamps (pd.DatetimeIndex): Index for timeseries data
        buildings (Dict[str, Building]): Dict of Building classes, organized by ID

    Attributes:
        asset_id (str): ID for the TEN
        annual_load_heating (list): The total annual heating load for the TEN, in kBTU
        annual_load_cooling (list): The total annual cooling load for the TEN, in kBTU
        annual_load_total (list): Sum of annual_heating_load and annual_cooling_load
        annual_peak_heating (list): The total annual peak heating demand, in kBTU/hr
        annual_peak_cooling (list): The total annual peak cooling demand, in kBTU/hr
        annual_peak_network (list): The max of annual_heating_peak and annual_cooling_peak

    Methods:
        create_network (None): Calculates network attributes
    """
    def __init__(
            self, years_vec: list,
            year_timestamps: pd.DatetimeIndex,
            buildings: Dict[str, Building]
    ):
        self._years_vec: list = years_vec
        self._year_timestamps: pd.DatetimeIndex = year_timestamps
        self._buildings: Dict[str, Building] = buildings

        self.asset_id: str = ""
        self.annual_load_heating: list = []
        self.annual_load_cooling: list = []
        self.annual_load_total: list = []
        self.annual_peak_heating: list = []
        self.annual_peak_cooling: list = []
        self.annual_peak_network: list = []

        #TODO: Add installation cost, book value, and O&M. Requires adding TEN config

    def create_network(self) -> None:
        """
        Calculate network attributes
        """
        self.asset_id = DEFAULT_TEN_ID

        self.annual_load_heating = self._calc_annual_load("heating")
        self.annual_load_cooling = self._calc_annual_load("cooling")
        self.annual_load_total = self._calc_annual_load_total()
        self.annual_peak_heating = self._calc_annual_peak("heating")
        self.annual_peak_cooling = self._calc_annual_peak("cooling")

    def _calc_annual_load(self, heating_cooling: str) -> list:
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
            annual_ten_load = bldg._annual_energy_by_fuel.get(f"thermal_{heating_cooling}")
            annual_load[bldg_id] = annual_ten_load

        annual_load = pd.DataFrame(annual_load, index=self._years_vec)
        return annual_load.sum(axis=1).to_list()
    
    def _calc_annual_load_total(self) -> list:
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
    
    def _calc_annual_peak(self, heating_cooling: str) -> list:
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
    
    def _calc_annual_peak_network(self) -> list:
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
