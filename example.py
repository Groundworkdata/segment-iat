"""
Example script of using the repo
"""
from scenario_creator.create_scenario import ScenarioCreator


def main():
    scenario = ScenarioCreator(
        "./config_files/simulation_settings_config.json",
        "./config_files/building_1_config.json",
        "./config_files/utility_network_config.json"
    )

    scenario.create_scenario()

    print(scenario.buildings["building001"].end_uses["stove"]["stove1"].depreciation)
    print(scenario.buildings["building001"].end_uses["stove"]["stove1"].stranded_value)
    print(scenario.buildings["building001"].end_uses["stove"]["stove2"].depreciation)
    print(scenario.buildings["building001"].end_uses["stove"]["stove2"].stranded_value)
    print("------------------")
    print(scenario.buildings["building001"].aggregate())
    print("------------------")
    print(scenario.utility_network.gas_meters[0].total_energy_use)
    print(scenario.utility_network.elec_meters[0].total_energy_use)

if __name__ == "__main__":
    main()
