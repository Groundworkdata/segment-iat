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

    def get_operational_vector(self) -> list:
        operational_vecs = []

        operational_vector = np.zeros(len(self.years_vector))
        operational_vecs.append(operational_vector)

        for asset in self.connected_assets:
            operational_vecs.append(np.array(asset.operational_vector))

        operational_vector = np.stack(operational_vecs).max(axis=0)

        return operational_vector.tolist()
    
    def _get_replacement_vec(self) -> List[bool]:
        replacement_vec = [False] * len(self.years_vector)
        replacement_idx = 0

        for asset in self.connected_assets:
            replaced = np.where(np.array(asset.operational_vector)==0)[0]
            # If size is zero, there is no replacement
            if replaced.size:
                replacement_idx = max(replacement_idx, replaced[0])

        if replacement_idx:
            replacement_vec[replacement_idx] = True

        return replacement_vec
