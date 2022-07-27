"""
Creates a scenario based on input values
"""
import numpy as np

from end_uses.building_end_uses.stove import Stove
from end_uses.meters.elec_meter import ElecMeter
from end_uses.meters.gas_meter import GasMeter


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
            elec_consump: float,
            gas_consump: float,
            sim_start_year: int,
            sim_end_year: int,
            replacement_year: int
    ):
        self.parcel_id = parcel_id
        self.install_year = install_year
        self.install_cost = install_cost
        self.lifetime = lifetime
        self.elec_consump = elec_consump
        self.gas_consump = gas_consump
        self.sim_start_year = sim_start_year
        self.sim_end_year = sim_end_year
        self.replacement_year = replacement_year
        self.energy_source = "ELEC"
        self.stove_type = "INDUCTION"

        self.end_uses: list = []
        self.meters: list = []

    def create_scenario(self):
        self.get_end_uses()
        self.get_meters()

    def get_end_uses(self):
        self.get_stoves()
        # Get other end uses: HVAC, washer/dryer, etc...

    def get_stoves(self):
        stove = Stove(
            self.install_year,
            self.install_cost,
            self.lifetime,
            self.elec_consump,
            self.gas_consump,
            self.sim_start_year,
            self.sim_end_year,
            self.replacement_year,
            self.energy_source,
            self.stove_type,
        )

        stove.initialize_end_use()

        self.end_uses.append(stove)

    def get_meters(self):
        self.get_elec_meter()
        self.get_gas_meter()

    def get_elec_meter(self):
        elec_meter = ElecMeter(self.end_uses)
        elec_meter.initialize_meter()
        self.meters.append(elec_meter)

    def get_gas_meter(self):
        gas_meter = GasMeter(self.end_uses)
        gas_meter.initialize_meter()
        self.meters.append(gas_meter)
