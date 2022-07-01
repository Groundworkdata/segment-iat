"""
Defines Stove end use
"""
import numpy as np

from end_uses.end_use import EndUse


class Stove(EndUse):
    """
    Stove end use

    Args:
        energy_source (str): In ["ELEC", "GAS", "PROPANE"]
        stove_type (str): In ["ELEC", "GAS", "INDUCTION"]
    """
    def __init__(
            self,
            install_year,
            install_cost,
            lifetime,
            energy_consump,
            sim_start_year,
            sim_end_year,
            energy_source: str,
            stove_type: str,
            replacement_year: int
    ):
        super().__init__(
            install_year,
            install_cost,
            lifetime,
            energy_consump,
            sim_start_year,
            sim_end_year,
            replacement_year
        )

        self.energy_source: str = energy_source
        self.stove_type: str = stove_type

    def get_install_cost(self) -> float:
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
        if self.energy_source != "ELEC":
            return np.zeros(len(self.operational_vector)).tolist()

        annual_elec_consump = 100
        elec_consump_esc = 0.01

        elec_consump = np.array([
            annual_elec_consump * ((1 + elec_consump_esc) ** (i - self.years_vector[0]))
            for i in self.years_vector
        ])

        return (elec_consump * np.array(self.operational_vector)).tolist()

    def get_gas_consump(self) -> list:
        if self.energy_source != "GAS":
            return np.zeros(len(self.operational_vector)).tolist()

        annual_gas_consump = 50
        gas_consump_esc = 0.01

        gas_consump = np.array([
            annual_gas_consump * ((1 + gas_consump_esc) ** (i - self.years_vector[0]))
            for i in self.years_vector
        ])

        return (gas_consump * np.array(self.operational_vector)).tolist()
