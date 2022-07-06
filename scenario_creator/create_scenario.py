"""
Creates a scenario based on input values
"""
import numpy as np

from end_uses.stove import Stove


class ScenarioCreator:
    """
    Create scenario for a parcel and tally total energy usages
    """
    def __init__(
            self,
            parcel_id: str,
            install_year: int,
            install_cost: float,
            lifetime: int,
            energy_consump: float,
            sim_start_year: int,
            sim_end_year: int,
            replacement_year: int
    ):
        self.parcel_id = parcel_id
        self.install_year = install_year
        self.install_cost = install_cost
        self.lifetime = lifetime
        self.energy_consump = energy_consump
        self.sim_start_year = sim_start_year
        self.sim_end_year = sim_end_year
        self.replacement_year = replacement_year
        self.energy_source = "ELEC"
        self.stove_type = "INDUCTION"

        self.end_uses: list = []
        self.total_elec_consump: list = []
        self.total_gas_consump: list = []

    def create_scenario(self):
        self.get_end_uses()
        self.total_elec_consump = self.get_elec_consump()
        self.total_gas_consump = self.get_gas_consump()

    def get_end_uses(self):
        self.get_stoves()
        # Get other end uses: HVAC, washer/dryer, etc...

    def get_stoves(self):
        stove = Stove(
            self.install_year,
            self.install_cost,
            self.lifetime,
            self.energy_consump,
            self.sim_start_year,
            self.sim_end_year,
            self.energy_source,
            self.stove_type,
            self.replacement_year
        )

        stove.initialize_end_use()

        self.end_uses.append(stove)

    def get_elec_consump(self):
        elec_consumps = [i.elec_consump for i in self.end_uses]
        return np.array(elec_consumps).sum(axis=0).tolist()

    def get_gas_consump(self):
        gas_consumps = [i.gas_consump for i in self.end_uses]
        return np.array(gas_consumps).sum(axis=0).tolist()
