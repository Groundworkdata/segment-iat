"""
Main script to run the simulation
"""
from scenario_creator.create_scenario import ScenarioCreator


def main():
    scenario = ScenarioCreator(
        "./config_files/simulation_settings_config.json"
    )

    scenario.create_scenario()

    print("Buildings: {}".format(list(scenario.buildings.keys())))
    print("==================")

if __name__ == "__main__":
    main()
