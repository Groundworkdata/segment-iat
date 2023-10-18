"""
Defines a gas meter
"""
import numpy as np

from ttt.end_uses.meters.meter import Meter


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
        decarb_scenario (str): The energy retrofit intervention scenario
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
            kwargs.get("decarb_scenario"),
            kwargs.get("building"),
            "natural_gas",
        )

        self._gas_shutoff: bool = kwargs.get("gas_shutoff_scenario", False)
        self._gas_shutoff_year: int = kwargs.get("gas_shutoff_year")
        self._retrofit_cost = kwargs.get("replacement_cost", DEFAULT_RETROFIT_COST)
        self._retrofit_freq = kwargs.get("replacement_freq", DEFAULT_RETROFIT_FREQ)

    def get_operational_vector(self) -> list:
        building_scenario = self.building.retrofit_scenario

        if self._gas_shutoff:
            return [
                1 if self.install_year <= i and self._gas_shutoff_year > i else 0
                for i in self.years_vector
            ]

        return [1] * len(self.years_vector)
    
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

        retrofit_years = [
            self._retrofit_freq*(i+1)-1
            for i in range(int(sim_length / self._retrofit_freq))
        ]

        retrofit_cost[retrofit_years] = self._retrofit_cost

        return (retrofit_cost * np.array(self.operational_vector)).tolist()
