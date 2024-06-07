"""
Defines gas main asset
"""
import numpy as np
import pandas as pd
from typing import List
import warnings

from ttt.end_uses.utility_end_uses.pipeline import Pipeline


DEFAULT_SHUTOFF_YEAR = 2100
DEFAULT_OM_COST = 0


class GasMain(Pipeline):
    """
    Defines a gas main pipeline, which inherits Pipeline class

    Args:
        None

    Keyword Args:
        gisid (str): The ID for the given asset
        parentid (str): The ID for the parent of the asset (if applicable, otherwise empty)
        inst_date (int): The install year of the asset
        inst_cost (float): The cost of the asset in present day dollars
            (or in $ from install year if installed prior to sim start)
        lifetime (int): Useful lifetime of the asset in years
        sim_start_year (int): The simulation start year
        sim_end_year (int): The simulation end year (exclusive)
        replacement_year (int): The replacement year of the asset
        decarb_scenario (str): The energy retrofit intervention scenario
        length_ft (int): Pipeline length in feet
        pressure (str): Rated pressure of the pipe
        diameter (str): Diameter of the pipe
        material (str): The pipe material
        connected_assets (list): List of associated downstream assets
        replacement_cost (float): The cost of replacing the gas meter
        shutoff_cost (float): The cost of pipeline shutoff

    Attributes:
        replacement_cost (float): Cost of gas main replacement
        shutoff_cost (float): Cost of gas main shutoff
        book_value (list): Annual book value of the gas main
        shutoff_year (list): 1 in the shutoff year, 0 all other years

    Methods:
        initialize_end_use (None): Executes all calculations for the meter
        get_operational_vector (list): Returns list of 1 if gas meter in use, 0 o/w, for all sim years
        get_retrofit_vector (list): Returns vector where value is 1 in the retrofit year, 0 o/w
        get_install_cost (list): Returns vector of install cost by sim year
        get_depreciation (list): Return the list of annual depreciated value for all sim years
        get_book_value (list): Returns annual book value vector
        get_shutoff_year (list): Returns vector with value 1 in shutoff year, 0 o/w
        get_system_shutoff_cost (list): Returns vector with the system shutoff cost by sim year
    """
    def __init__(self, **kwargs):
        super().__init__(
            kwargs.get("gisid"),
            kwargs.get("parentid"),
            kwargs.get("inst_date"),
            kwargs.get("inst_cost"),
            kwargs.get("lifetime"),
            kwargs.get("sim_start_year"),
            kwargs.get("sim_end_year"),
            kwargs.get("replacement_year"),
            kwargs.get("decarb_scenario"),
            kwargs.get("length_ft"),
            kwargs.get("pressure"),
            kwargs.get("diameter"),
            kwargs.get("material"),
            kwargs.get("connected_assets"),
            kwargs.get("segment_id"),
            "gas_main",
        )

        self._gas_shutoff: bool = kwargs.get("gas_shutoff_scenario", False)
        self._gas_shutoff_year: int = kwargs.get("gas_shutoff_year", DEFAULT_SHUTOFF_YEAR)
        self._gas_replacement_year: bool = kwargs.get("replacement_year")
        self.replacement_cost = kwargs.get("replacement_cost", 0)
        self.shutoff_cost = kwargs.get("shutoff_cost", 0)
        self.book_value: list = []
        self.shutoff_year: list = []

    def initialize_end_use(self) -> None:
        super().initialize_end_use()
        self.book_value = self.get_book_value()
        self.shutoff_year = self.get_shutoff_year()
        self.stranded_value = self._update_stranded_value()
        self.annual_operating_expenses = self._get_annual_om()

    def get_operational_vector(self) -> list:
        operational_vecs = []

        operational_vector = np.zeros(len(self.years_vector))
        operational_vecs.append(operational_vector)

        for asset in self.connected_assets:
            operational_vecs.append(np.array(asset.operational_vector))

        operational_vector = np.stack(operational_vecs).max(axis=0)

        return operational_vector.tolist()

    def _get_replacement_vec(self) -> List[bool]:
        # Replacement must be specifically input
        replacement_vec = [False] * len(self.years_vector)

        if self._gas_replacement_year:
            replacement_vec[self._gas_replacement_year - self.sim_start_year] = True

        return replacement_vec

    def get_retrofit_vector(self) -> list:
        retrofit_vector = np.zeros(len(self.years_vector))

        if self._gas_replacement_year:
            retrofit_vector[self._gas_replacement_year - self.sim_start_year:] = 1

        return retrofit_vector.astype(bool).tolist()

    def get_install_cost(self) -> list:
        install_cost = np.zeros(len(self.years_vector))

        if self._gas_replacement_year:
            install_cost[self._gas_replacement_year - self.sim_start_year] = self.replacement_cost

        return install_cost.tolist()

    def get_depreciation(self) -> List[float]:
        depreciation = np.zeros(len(self.years_vector))

        if self._gas_replacement_year:
            depreciation_rate = self.replacement_cost / self.lifetime
            depreciation[self._gas_replacement_year - self.sim_start_year:] = [
                max(self.replacement_cost - depreciation_rate * i, 0)
                for i in range(self.sim_end_year - self._gas_replacement_year)
            ]

        return depreciation.tolist()

    def get_book_value(self) -> List[float]:
        return self.depreciation

    def get_shutoff_year(self) -> List[float]:
        #FIXME: If there is a connected asset still on gas outside of the simulation timeframe,
        # this will shutoff the main in the last year of gas usage WITHIN the timeframe
        # This is because the function does not look at gas usage outside of the sim timeframe;
        # it only references each connected asset's _retrofit_vec, which is over the timeframe only
        # For example, if we run a gas shutoff scenario where the sim goes to 2050 (exclusive)
        # and there is a parcel still on gas in 2053, the model will not account for this and 
        # shut off the main in the latest year before 2050 that gas usage stops in connected assets
        shutoff_year_vec = [0] * len(self.years_vector)

        if self._gas_shutoff:
            shutoff_year = 0
            for service in self.connected_assets:
                building = service.connected_assets[0].building

                for idx, retrofit in enumerate(building._retrofit_vec):
                    if retrofit:
                        shutoff_year = max(shutoff_year, idx)

            if shutoff_year:
                shutoff_year_vec[shutoff_year] = 1

        return shutoff_year_vec

    def _update_stranded_value(self) -> List[float]:
        return (np.array(self.book_value) * np.array(self.shutoff_year)).tolist()
    
    def get_system_shutoff_cost(self) -> List[float]:
        return (np.array(self.shutoff_year) * self.shutoff_cost).tolist()

    def _get_annual_om(self) -> List[float]:
        om_filepath = f"./config_files/{self._segment_id}/utility_network/{self._segment_id}_operating_expenses.csv"
        om_table = pd.read_csv(om_filepath)

        annual_operating_expense = om_table[
            (om_table["type"]==self.pipeline_type)
            & (om_table["material"]==self.material)
        ]["operating_expense_per_mile"].to_dict().get(0, DEFAULT_OM_COST)

        if not annual_operating_expense:
            warnings.warn(
                f"Material {self.material.upper()} not in O&M table for pipeline type {self.pipeline_type.upper()}! Using default ${DEFAULT_OM_COST} / year."
            )

        # Convert length in feet to miles
        annual_operating_expense = annual_operating_expense * (self.length / 5280)

        return (annual_operating_expense * np.array(self.operational_vector)).tolist()
