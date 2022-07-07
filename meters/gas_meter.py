"""
Defines a gas meter
"""
from meters.meter import Meter


class GasMeter(Meter):
    """
    Defines a gas meter, which inherits Meter class

    Args:
        end_uses (list): List of end use instances (Stove, etc)
    """
    def __init__(self, end_uses: list):
        super().__init__(end_uses, "GAS")
