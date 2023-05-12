"""
Defines Mains end use
"""
import numpy as np
from typing import List

from end_uses.utility_end_uses.pipeline import Pipeline


class GasMain(Pipeline):
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
            kwargs.get("length_ft"),
            kwargs.get("pressure"),
            kwargs.get("diameter"),
            kwargs.get("material"),
            kwargs.get("connected_assets"),
            "gas_main",
        )
