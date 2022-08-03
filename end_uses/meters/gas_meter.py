"""
Defines a gas meter
"""
from end_uses.meters.meter import Meter


class GasMeter(Meter):
    """
    Defines a gas meter, which inherits Meter class

    Args:
        end_uses (list): List of end use instances (Stove, etc)

    Keyword Args:
        install_year (int): Installation year
        asset_cost (float): Cost of the meter
        replacement_year (int): Replacement year
        lifetime (int): Asset lifetime in years
        sim_start_year (int): Simulation start year
        sim_end_year (int): Simulation end year (exclusive)
        asset_id (str): ID of the meter asset
        parent_id (str): ID of the meter's parent in the utility network
        building_id (str)
        building (Building)

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
            "GAS"
        )
