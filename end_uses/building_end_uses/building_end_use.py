"""
EndUse parent class
"""
import numpy as np

from end_uses.asset import Asset


class BuildingEndUse(Asset):
    """
    Defines the parent BuildingEndUse class for all building-level end uses. Inherits from Asset

    Args:
        None

    Keyword Args:
        install_year (int): The install year of the asset
        asset_cost (float): The cost of the asset in present day dollars
            (or in $ from install year if installed prior to sim start)
        replacement_year (int): The replacement year of the asset
        lifetime (int): The asset lifetime in years
        sim_start_year (int): The simulation start year
        sim_end_year (int): The simulation end year (exclusive)
        elec_consump (float): The total annual elec consump, in kWh
        gas_consump (float): The total annual gas consump, in kWh
        building_id (str): Identifies the building where the end use is located

    Attributes:
        install_year (int): The install year of the asset
        asset_cost (float): The cost of the asset in present day dollars
            (or in $ from install year if installed prior to sim start)
        replacement_year (int): The replacement year of the asset
        lifetime (int): The asset lifetime in years
        sim_start_year (int): The simulation start year
        sim_end_year (int): The simulation end year (exclusive)
        years_vector (list): List of all years for the simulation
        operational_vector (list): Boolean vals for years of the simulation when asset in operation
        install_cost (list): Install cost during the simulation years
        depreciation (list): Depreciated val during the simulation years
            (val is depreciated val at beginning of each year)
        stranded_value (list): Stranded asset val for early replacement during the simulation years
            (equal to the depreciated val at the replacement year)
        elec_consump (float): The total annual elec consump, in kWh
        gas_consump (float): The total annual gas consump, in kWh
        total_elec_consump (list): The total annual elec consump of the end use, in kWh
        total_gas_consump (list): The total annual gas consump of the end use, in kWh
        gas_leakage (list): List of annual gas leakage from end use, in kWh
        building_id (str): Identifies the building where the end use is located

    Methods:
        initialize_end_use (None): Performs all calculations for the end use
    """
    def __init__(self, **kwargs):
        super().__init__(
            kwargs.get("install_year"),
            kwargs.get("asset_cost"),
            kwargs.get("replacement_year"),
            kwargs.get("lifetime"),
            kwargs.get("sim_start_year"),
            kwargs.get("sim_end_year")
        )

        #TODO: Need to decide what to do with install cost
        # If it is an existing end-use, then we should intake the install cost total and no calc needed
        # If new end-use, then we intake multiple cost factors (current sticker price, labor rate, escalator) and calc total cost
        self.asset_cost: float = kwargs.get("asset_cost")
        self.lifetime: int = kwargs.get("lifetime")
        self.elec_consump = kwargs.get("elec_consump")
        self.gas_consump = kwargs.get("gas_consump")
        self.building_id: str = kwargs.get("building_id")

        self.total_elec_consump: list = []
        self.total_gas_consump: list = []
        self.gas_leakage: list = []

    def initialize_end_use(self) -> None:
        """
        Expands on parent initialize_end_use method to calculate additional values
        """
        super().initialize_end_use()
        self.elec_consump_total = self.get_elec_consump()
        self.gas_consump_total = self.get_gas_consump()
        self.gas_leakage = self.get_gas_leakage()

    def get_elec_consump(self) -> list:
        # TODO: Decide on format and populate with dummy data
        return (np.ones(len(self.operational_vector)) * np.array(self.operational_vector)).tolist()

    def get_gas_consump(self) -> list:
        # TODO: Decide on format and populate with dummy data
        return (np.ones(len(self.operational_vector)) * np.array(self.operational_vector)).tolist()

    def get_gas_leakage(self) -> list:
        """
        Assume no gas leakage by default
        """
        return np.zeros(len(self.operational_vector)).tolist()
