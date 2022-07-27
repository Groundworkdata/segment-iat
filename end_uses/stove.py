"""
Defines Stove end use
"""
import numpy as np

from end_uses.building_end_use import BuildingEndUse


class Stove(BuildingEndUse):
    """
    Stove end use. Inherits parent BuildingEndUse class

    Args:
        energy_source (str): In ["ELEC", "GAS", "PROPANE"]
        stove_type (str): In ["ELEC", "GAS", "INDUCTION"]

    Methods:
        get_install_cost (float): Calculates the stove install cost. Overwrites parent method
        get_elec_consump (list): Calculates the stove elec consumption. Overwrites parent method
        get_gas_cost (list): Calculates the stove gas consumption. Overwrites parent method
    """
    def __init__(
            self,
            install_year,
            install_cost,
            lifetime,
            elec_consump,
            gas_consump,
            sim_start_year,
            sim_end_year,
            replacement_year: int,
            energy_source: str,
            stove_type: str,
    ):
        super().__init__(
            install_year,
            install_cost,
            lifetime,
            elec_consump,
            gas_consump,
            sim_start_year,
            sim_end_year,
            replacement_year
        )

        self.energy_source: str = energy_source
        self.stove_type: str = stove_type

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

        return (total_labor + total_material) * escalation_factor

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

    def get_depreciation(self) -> list:
        """
        Uses straight line depreciation and assumes no salvage value at end-of-life. Overwrites
        parent method

        Vector represents depreciated end use value at year-beginning
        """
        salvage_value = 0
        depreciation_rate = (self.end_use_cost - salvage_value) / self.lifetime

        operational_lifetime = self.replacement_year - self.install_year

        depreciated_value = np.array([
            self.end_use_cost - depreciation_rate * i
            for i in range(operational_lifetime+1)
        ])

        start_zeros_vec = np.zeros(max(self.install_year - self.sim_start_year, 0))

        clipped_dep_vec = depreciated_value[
            max(self.sim_start_year - self.install_year, 0):
            max(operational_lifetime-(self.replacement_year-self.sim_end_year), 0)
        ]

        end_zeros_vec = np.zeros(max(self.sim_end_year-self.replacement_year-1, 0))

        depreciation_vec = np.concatenate([start_zeros_vec, clipped_dep_vec, end_zeros_vec])
        return depreciation_vec.tolist()

    def get_stranded_value(self) -> list:
        """
        Calculates the stranded value based on the depreciation vector. Overwrites parent method

        Depreciation value and replacement is year-beginning, so references depreciated value at the
        replacement year

        Stranded value is 0 if the replacement year is outside of the sim timeframe
        """
        replacement_ref = self.replacement_year - self.sim_start_year
        operational_lifetime = self.replacement_year - self.install_year

        stranded_val = np.zeros(len(self.operational_vector))

        # Handle when the replacement year is beyond the simulation end year
        if self.replacement_year > self.sim_end_year:
            return stranded_val.tolist()

        # Handle if replacement in final year and not fully depreciated
        elif self.replacement_year == self.sim_end_year and operational_lifetime != self.lifetime:
            replacement_ref = -1

        # Handle if replacement in final year and fully depreciated
        elif self.replacement_year == self.sim_end_year and operational_lifetime == self.lifetime:
            return stranded_val.tolist()

        stranded_val[replacement_ref] = self.depreciation[replacement_ref]
        return stranded_val.tolist()
