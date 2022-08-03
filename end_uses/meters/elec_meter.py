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
            kwargs.get("install_year"),
            kwargs.get("asset_cost"),
            kwargs.get("replacement_year"),
            kwargs.get("lifetime"),
            kwargs.get("sim_start_year"),
            kwargs.get("sim_end_year"),
            kwargs.get("asset_id"),
            kwargs.get("parent_id"),
            kwargs.get("building_id"),
            kwargs.get("building"),
            "ELEC"
        )
