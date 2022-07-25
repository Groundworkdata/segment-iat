"""
Defines UtilityEndUse parent class
"""
from end_uses.asset import Asset


class UtilityEndUse(Asset):
    """
    UtilityEndUse parent class
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
            parent_id
    ):
        super().__init__(
            install_year,
            asset_cost,
            replacement_year,
            lifetime,
            sim_start_year,
            sim_end_year
        )
        self.asset_id = asset_id
        self.parent_id = parent_id
