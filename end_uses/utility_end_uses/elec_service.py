"""
Defines Electricity Service end use
"""
import numpy as np
from typing import List

from end_uses.utility_end_uses.distribution_lines import DistributionLine


class ElecService(DistributionLine):
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
