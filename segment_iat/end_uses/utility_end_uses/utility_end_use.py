"""
Defines UtilityEndUse parent class
"""
from segment_iat.end_uses.asset import Asset


class UtilityEndUse(Asset):
    """
    UtilityEndUse parent class

    Args:
        gisid (str): The ID for the given asset
        parent_id (str): The ID for the parent of the asset (if applicable, otherwise empty)
        inst_date (int): The install year of the asset
        inst_cost (float): The cost of the asset in present day dollars
            (or in $ from install year if installed prior to sim start)
        lifetime (int): The asset lifetime in years
        sim_start_year (int): The simulation start year
        sim_end_year (int): The simulation end year (exclusive)
        replacement_year (int): The replacement year of the asset

    Attributes:
        asset_id (str): The ID for the given asset
        parent_id (str): The ID for the parent of the asset (if applicable, otherwise empty)

    Methods:
        None
    """

    def __init__(
        self,
        gisid,
        parentid,
        inst_date,
        inst_cost,
        lifetime,
        sim_start_year,
        sim_end_year,
        replacement_year,
    ):
        super().__init__(
            inst_date,
            inst_cost,
            lifetime,
            sim_start_year,
            sim_end_year,
            replacement_year,
        )

        self.asset_id = gisid
        self.parent_id = parentid
