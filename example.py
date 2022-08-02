"""
Example script of using the repo
"""
from scenario_creator.create_scenario import ScenarioCreator


def main():
    scenario = ScenarioCreator(
        "./config_files/simulation_settings_config.json",
        "./config_files/building_1_config.json"
    )

    scenario.create_scenario()

    print(scenario.meters[0].total_energy_use)
    print(scenario.meters[1].total_energy_use)
    print(scenario.buildings[0].end_uses["stove"]["stove1"].depreciation)
    print(scenario.buildings[0].end_uses["stove"]["stove1"].stranded_value)
    print(scenario.buildings[0].end_uses["stove"]["stove2"].depreciation)
    print(scenario.buildings[0].end_uses["stove"]["stove2"].stranded_value)
    print("------------------")
    print(scenario.buildings[0].aggregate())

if __name__ == "__main__":
    main()
