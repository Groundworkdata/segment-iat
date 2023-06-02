"""
Defines a gas meter
"""
from end_uses.meters.meter import Meter


GAS_SHUTOFF_SCENARIOS = ["natural_elec", "accelerated_elec", "hybrid_npa"]


class GasMeter(Meter):
    """
    Defines a gas meter, which inherits Meter class

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
        asset_id (str): The ID for the given asset
        parent_id (str): The ID for the parent of the asset (if applicable, otherwise empty)
        building_id (str): The ID of the associated building for the meter
        building (Building): Instance of the associated Building object

    Methods:
        None
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

    def get_operational_vector(self) -> list:
        building_scenario = self.building.retrofit_scenario

        if building_scenario in GAS_SHUTOFF_SCENARIOS:
            return [
                1 if self.install_year <= i and self.replacement_year > i else 0
                for i in self.years_vector
            ]
        
        return [1] * len(self.years_vector)
