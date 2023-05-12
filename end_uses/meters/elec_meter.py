"""
Defines an electric meter
"""
from end_uses.meters.meter import Meter


class ElecMeter(Meter):
    """
    Defines an electric meter, which inherits Meter class

    Args:
        None

    Keyword Args:
        inst_date (int): The install year of the asset
        inst_cost (float): The cost of the asset in present day dollars
            (or in $ from install year if installed prior to sim start)
        replacement_year (int): The replacement year of the asset
        lifetime (int): The asset lifetime in years
        sim_start_year (int): The simulation start year
        sim_end_year (int): The simulation end year (exclusive)
        gisid (str): The ID for the given asset
        parentid (str): The ID for the parent of the asset (if applicable, otherwise empty)
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
            "electricity",
        )

        self.solar: bool = kwargs.get("solar")
        self.type: str = kwargs.get("type")
