"""
Defines UtilityEndUse parent class
"""
from end_uses.asset import Asset


class UtilityEndUse(Asset):
    """
    UtilityEndUse parent class

    Args:
        install_year (int): The install year of the asset
        asset_cost (float): The cost of the asset in present day dollars
            (or in $ from install year if installed prior to sim start)
        replacement_year (int): The replacement year of the asset
        lifetime (int): The asset lifetime in years
        sim_start_year (int): The simulation start year
        sim_end_year (int): The simulation end year (exclusive)
        asset_id (str): The ID for the given asset
        parent_id (str): The ID for the parent of the asset (if applicable, otherwise empty)

    Attributes:
        install_year (int): The install year of the asset
        asset_cost (float): The cost of the asset in present day dollars
            (or in $ from install year if installed prior to sim start)
        replacement_year (int): The replacement year of the asset
        lifetime (int): The asset lifetime in years
        sim_start_year (int): The simulation start year
        sim_end_year (int): The simulation end year (exclusive)
        years_vector (list): List of all years for the simulation
        operational_vector (list): Boolean vals for years of the simulation when asset in operation
        install_cost (list): Install cost during the simulation years
        depreciation (list): Depreciated val during the simulation years
            (val is depreciated val at beginning of each year)
        stranded_value (list): Stranded asset val for early replacement during the simulation years
            (equal to the depreciated val at the replacement year)
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
