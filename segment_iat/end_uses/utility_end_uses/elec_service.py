"""
Defines electricity service end use
"""
from segment_iat.end_uses.utility_end_uses.distribution_lines import DistributionLine


class ElecService(DistributionLine):
    """
    An electric service line

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
        connected_assets (list): List of associated downstream assets
        circuit (int): The electric circuit ID
        oh_ug (str): Signifies if overhead (OH) or underground (UG) wire
        phase (str): Phase rotation of the line (ABC or ACB)
        sec_wsize (int): The wire size
        sec_wtype (str): Wire type

    Attributes:
        circuit (int): The electric circuit ID
        oh_ug (str): Signifies if overhead (OH) or underground (UG) wire
        phase (str): Phase rotation of the line (ABC or ACB)
        sec_wsize (int): The wire size
        sec_wtype (str): Wire type

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
            kwargs.get("connected_assets"),
            "elec_service",
        )

        self.circuit: int = kwargs.get("circuit")
        self.oh_ug: str = kwargs.get("oh_ug")
        self.phase: str = kwargs.get("phase")
        self.sec_wsize: int = kwargs.get("sec_wsize")
        self.sec_wtype: str = kwargs.get("sec_wtype")
