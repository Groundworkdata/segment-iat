"""
Defines Stove end use
"""
import numpy as np

from end_uses.building_end_uses.building_end_use import BuildingEndUse


class Stove(BuildingEndUse):
    """
    Stove end use. Inherits parent BuildingEndUse class

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
        energy_source (str): In ["ELEC", "GAS", "PROPANE"]
        stove_type (str): In ["ELEC", "GAS", "INDUCTION"]

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
        energy_source (str): In ["ELEC", "GAS", "PROPANE"]
        stove_type (str): In ["ELEC", "GAS", "INDUCTION"]

    Methods:
        get_install_cost (float): Calculates the stove install cost. Overwrites parent method
        get_elec_consump (list): Calculates the stove elec consumption. Overwrites parent method
        get_gas_cost (list): Calculates the stove gas consumption. Overwrites parent method
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.energy_source: str = kwargs.get("energy_source")
        self.stove_type: str = kwargs.get("stove_type")

    def get_install_cost(self) -> float:
        """
        Calculates installation cost for a stove. Overwrites parent method

        Stove installation cost is as follows:
            (labor removal rate) * (labor time)
            + ((new stove price) + (miscellaneous supplies price)) * (1 + (retail markup percent))
            + (labor installation rate) * (labor time)

        All rates are in today's dollars. Total stove installation cost is multiplied by an annual
        escalation factor to get cost for the corresponding installation year
        """
        # TODO: Abstract inputs so we are not using the defaults here
        removal_labor_time = 2 # hr
        labor_rate = 50 # 2019$ / hr
        existing_removal_labor = removal_labor_time * labor_rate

        new_stove_price = 900 # 2019$
        misc_supplies_price = 100 # 2019$
        retail_markup = 0.18 # percent
        new_stove_material = (new_stove_price + misc_supplies_price) * (1 + retail_markup)

        installation_labor_time = 2 # hr
        installation_labor = installation_labor_time * labor_rate

        total_labor = existing_removal_labor + installation_labor
        total_material = new_stove_material

        escalator = 0.01 # percent
        escalation_factor = (1 + escalator) ** (self.install_year - self.sim_start_year)

        total_cost = (total_labor + total_material) * escalation_factor

        install_cost = np.zeros(len(self.operational_vector)).tolist()
        # If the install is outside of the sim years, then we ignore the install cost
        if self.sim_start_year <= self.install_year <= self.sim_end_year:
            install_cost[self.install_year - self.sim_start_year] = total_cost

        return install_cost

    def get_elec_consump(self) -> list:
        """
        Calculates the elctric consumption for the stove. Overwrites parent method

        Electric consumption is based on an input annual consumption and then escalated by some
        factor for each year of operation.

        TODO: Replace annual consumption with a more granular timeseries
        """
        # TODO: Remove escalation
        elec_consump_esc = 0.01

        elec_consump = np.array([
            self.elec_consump * ((1 + elec_consump_esc) ** (i - self.years_vector[0]))
            for i in self.years_vector
        ])

        return (elec_consump * np.array(self.operational_vector)).tolist()

    def get_gas_consump(self) -> list:
        """
        Calculates the gas consumption for the stove. Overwrites parent method

        Gas consumption is based on an input annual consumption and then escalated by some
        factor for each year of operation.

        TODO: Replace annual consumption with a more granular timeseries
        """
        # TODO: Remove escalation
        gas_consump_esc = 0.01

        gas_consump = np.array([
            self.gas_consump * ((1 + gas_consump_esc) ** (i - self.years_vector[0]))
            for i in self.years_vector
        ])

        return (gas_consump * np.array(self.operational_vector)).tolist()

    def get_gas_leakage(self) -> list:
        """
        Gets annual gas leakage for the stove. Overwrites parent method. Currently defaulted
        """
        # TODO: Will need to input a leakage rate and include any escalation
        return np.repeat(50, len(self.operational_vector))
