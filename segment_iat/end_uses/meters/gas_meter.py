"""
Defines a gas meter
"""
import numpy as np

from segment_iat.end_uses.meters.meter import Meter


GAS_SHUTOFF_SCENARIOS = [
    "natural_elec", "accelerated_elec",
    "natural_elec_higheff", "accelerated_elec_higheff",
    "hybrid_npa"
]
DEFAULT_RETROFIT_FREQ = 7
DEFAULT_RETROFIT_COST = 1000


class GasMeter(Meter):
    """
    Defines a gas meter, which inherits Meter class

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
        building (Building): Instance of the associated Building object
        replacement_cost (float): The cost of replacing the gas meter
        replacement_freq (int): The annual frequency at which the gas meter is replaced

    Attributes:
        None

    Methods:
        get_operational_vector (list): Returns list of 1 if gas meter in use, 0 o/w, for all sim years
        get_depreciation (list): Return the list of annual depreciated value for all sim years
        get_retrofit_cost (list): Return list of annual retrofit cost for all sim years
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
            kwargs.get("building"),
            "natural_gas",
        )

        self._gas_intervention_year: int = kwargs.get("gas_pipe_intervention_year")
        self._gas_intervention: str = kwargs.get("gas_intervention")
        self._gas_shutoff: bool = self._gas_intervention.lower()=="decommission"
        self._retrofit_cost = kwargs.get("replacement_cost", DEFAULT_RETROFIT_COST)
        self._retrofit_freq = kwargs.get("replacement_freq", DEFAULT_RETROFIT_FREQ)

    def get_operational_vector(self) -> list:
        """
        Use building fuel to determine if there is still gas or not
        Take min of first year without gas and self._gas_shutoff_year

        Building _fuel_type can take values of: [GAS, OIL, ELEC, LPG, HPL, NPH]
        """
        building_fuel = self.building._fuel_type

        final_gas_year = self.sim_start_year - 1
        if "GAS" in building_fuel:
            final_gas_year = (
                len(building_fuel) - building_fuel[::-1].index("GAS")
                + self.sim_start_year
            )

        gas_shutoff_year = self.sim_end_year
        if final_gas_year < self.sim_end_year or self._gas_shutoff:
            gas_shutoff_year = min(final_gas_year+1, self._gas_intervention_year)

        return [
            1 if self.install_year <= i and gas_shutoff_year > i else 0
            for i in self.years_vector
        ]
    
    def get_depreciation(self) -> list:
        """
        Assume fully depreciated at all time
        """
        return np.zeros(len(self.years_vector)).tolist()
    
    def get_retrofit_cost(self) -> list:
        """
        Assume a regular schedule of retrofit costs
        """
        sim_length = len(self.years_vector)
        retrofit_cost = np.zeros(sim_length)

        if self._retrofit_freq == 0:
            if not self._gas_shutoff:
                retrofit_index = self._gas_intervention_year - self.sim_start_year
                retrofit_years = retrofit_index
            else:
                retrofit_years = []

        else:
            retrofit_years = [
                self._retrofit_freq*(i+1)-1
                for i in range(int(sim_length / self._retrofit_freq))
            ]

        retrofit_cost[retrofit_years] = self._retrofit_cost

        return (retrofit_cost * np.array(self.operational_vector)).tolist()
