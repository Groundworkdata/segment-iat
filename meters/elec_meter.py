"""
Defines an electric meter
"""
from meters.meter import Meter


class ElecMeter(Meter):
    """
    Defines an electric meter, which inherits Meter class

    Args:
        end_uses (list): List of end use instances (Stove, etc)
    """
    def __init__(self, end_uses: list):
        super().__init__(end_uses, "ELEC")
