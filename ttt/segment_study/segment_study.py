"""
Defines a SegmentStudy class
"""
import os

import pandas as pd


class SegmentStudy:
    """
    A pipeline segment study

    Args:
        segment_name (str): The name of the segment
        study_start_year (str): The start year of the study
        study_end_year (str): The end year of the study
        gas_pipe_intervention_year (str): The year for gas pipe intervention

    Attributes:
        segment_name (str): The name of the segment
        study_start_year (int): The start year of the study
        study_end_year (int): The end year of the study
        gas_pipe_intervention_year (int): The year for gas pipe intervention

    Methods:
        None
    """
    def __init__(
            self,
            segment_name: str,
            study_start_year: str,
            study_end_year: str,
            gas_pipe_intervention_year: str
    ) -> None:
        self.segment_name: str = segment_name
        self.study_start_year: int = int(study_start_year)
        self.study_end_year: int = int(study_end_year)
        self.gas_pipe_intervention_year: int = int(gas_pipe_intervention_year)

        self._study_basepath = f"./config_files/{self.segment_name}"
        self.parcels_table: dict = {}


    def load_study(self):
        self.parcels_table = self._get_parcels_table()

    def _get_parcels_table(self) -> dict:
        parcels_filepath = os.path.join(self._study_basepath, "parcels/parcels.csv")
        parcels_df = pd.read_csv(parcels_filepath, index_col="parcel_id").to_dict(orient="index")
        return parcels_df
