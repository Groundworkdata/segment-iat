"""
Simple script for post-processing output tables from multiple runs
"""
import os

import pandas as pd


def main():
    """
    Post-processing script for combining output tables across scenarios
    """
    scenarios = [
        "accelerated_elec",
        "continued_gas",
        "hybrid_gas",
        "hybrid_npa",
        "natural_elec",
        "hybrid_gas_immediate",
    ]

    output_files = [
        "book_val",
        "consumption_costs",
        "consumption_emissions",
        "energy_consumption",
        "existing_stranded_val",
        "fuel_type",
        "is_retrofit_vec_table",
        "methane_leaks",
        "operating_costs",
        "peak_consump",
        "retrofit_cost",
        "retrofit_year",
    ]

    output_dir = "./outputs_combined/scenarios/combined/"

    for f in output_files:
        output_dfs = []
        for scenario in scenarios:
            filepath = os.path.join(f"./outputs_combined/scenarios/{scenario}/", f"{f}.csv")
            output_df = pd.read_csv(filepath)
            output_df.loc[:, "scenario"] = scenario
            output_dfs.append(output_df)

        combined_output = pd.concat(output_dfs)
        combined_output.to_csv(os.path.join(output_dir, f"{f}.csv"), index=False)



if __name__ == "__main__":
    main()
