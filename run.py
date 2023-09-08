"""
Main script to run the simulation
"""
from ttt.scenario_creator.create_scenario import ScenarioCreator


def main():
    street_segment = "mf"

    allowable_scenarios = [
        "continued_gas",
        "accelerated_elec",
        "accelerated_elec_higheff",
        "natural_elec",
        "natural_elec_higheff",
        "hybrid_gas",
        "hybrid_gas_immediate",
        "hybrid_npa"
    ]

    for scenario in allowable_scenarios:
        print(f"==========Running scenario {scenario}==========")

        scenario_creator = ScenarioCreator(
            f"./config_files/settings/doer_{street_segment}_{scenario}.json"
        )

        scenario_creator.create_scenario()

        print("Buildings: {}".format(list(scenario_creator.buildings.keys())))
        print("==================")

if __name__ == "__main__":
    main()
