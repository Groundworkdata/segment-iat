"""
Defines an electric meter
"""
from end_uses.meters.meter import Meter


class ElecMeter(Meter):
    """
    Defines an electric meter, which inherits Meter class

    Args:
        end_uses (list): List of end use instances (Stove, etc)
    """
    def __init__(
            self,
            install_year,
            asset_cost,
            replacement_year,
            lifetime,
            sim_start_year,
            sim_end_year,
            asset_id,
            parent_id,
            end_uses: list
    ):
        super().__init__(
            install_year,
            asset_cost,
            replacement_year,
            lifetime,
            sim_start_year,
            sim_end_year,
            asset_id,
            parent_id,
            end_uses,
            "ELEC"
        )
