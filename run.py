"""
Main script to run the simulation
"""
import argparse
import os
from typing import List

import pandas as pd

from ttt.scenario_creator.create_scenario import ScenarioCreator


OUTPUT_FILES = [
    "book_val",
    "consumption_costs",
    "consumption_emissions",
    "energy_consumption",
    "fuel_type",
    "is_retrofit_vec_table",
    "methane_leaks",
    "operating_costs",
    "peak_consump",
    "retrofit_cost",
    "retrofit_year",
    "stranded_val"
]

COMBINED_FILES_KEY = "combined"


def main():
    parser = argparse.ArgumentParser(
        description="Groundwork local energy asset planning model"
    )

    parser.add_argument("scenario", nargs="+", help="The scenario(s) you would like to run")
    parser.add_argument(
        "--postprocessing",
        help="Postprocess outputs across scenarios into condensed files to be tracked by git",
        action="store_true"
    )
    args = parser.parse_args()

    scenarios = args.scenario
    postprocessing = args.postprocessing

    print("==========Simulation pre-check==========")
    for scenario in scenarios:

        # FIXME: Update after final changes
        settings_filepath = f"./config_files/scenarios/{scenario}.json"
        settings_exist = os.path.exists(settings_filepath)

        if not settings_exist:
            raise FileNotFoundError(f"Settings files does not exist for scenario {scenario}")
    
    print("Check complete!")

    street_segments = []
    for scenario in scenarios:
        print(f"==========Scenario: {scenario}==========")
        print("Loading inputs...")

        # FIXME: Update after final changes
        settings_filepath = f"./config_files/scenarios/{scenario}.json"
        scenario_creator = ScenarioCreator(settings_filepath)

        scenario_creator.create_scenario()

        print("Buildings: {}".format(list(scenario_creator.buildings.keys())))
        print("==================")
        street_segments.append(scenario_creator.street_segment)

    print("==========Summary==========")
    print(f"The following scenarios were successfully executed: {scenarios}")

    post_process_outputs(postprocessing, street_segments)


def post_process_outputs(postprocessing: bool, street_segments: List[str]) -> None:
    """
    Post-processing of results from multiple scenarios

    Args:
        post_processing (bool): True if the user wants postprocessing performed
        street_segments (List[str]): List of street segments simulated

    Returns:
        None
    """
    if postprocessing:
        print("==========Postprocessing==========")
        street_segments_unique = set(street_segments)

        if len(street_segments_unique) > 1:
            print("Cannot combine results across segments!")
            print(f"The following street segments were simulated: {street_segments_unique}")

        for segment in street_segments_unique:
            outputs_filepath = os.path.join("./outputs", segment)
            scenario_folders = os.listdir(outputs_filepath)

            # combined_outputs_filepath = os.path.join(outputs_filepath, COMBINED_FILES_KEY)
            combined_outputs_filepath = f"./results/{segment}"
            if not os.path.exists(combined_outputs_filepath):
                os.makedirs(combined_outputs_filepath)

            for output_file in OUTPUT_FILES:
                output_dfs = []
                for scenario in scenario_folders:
                    if scenario == COMBINED_FILES_KEY:
                        break

                    filepath = os.path.join(outputs_filepath, scenario, f"{output_file}.csv")
                    output_df = pd.read_csv(filepath)
                    output_df.loc[:, "scenario"] = scenario
                    output_dfs.append(output_df)

                combined_output = pd.concat(output_dfs)
                combined_output.to_csv(
                    os.path.join(combined_outputs_filepath, f"{output_file}.csv"),
                    index=False
                )

            print(f"Postprocessing for {segment} segment complete!")
        print("Postprocessing results complete!")



if __name__ == "__main__":
    main()
