"""
Example script of using the repo
"""
from scenario_creator.create_scenario import ScenarioCreator


def main():
    scenario = ScenarioCreator(
        "./config_files/simulation_settings_config.json",
        "./config_files/buildings_config.json",
        "./config_files/utility_network_config.json"
    )

    scenario.create_scenario()

    print("Buildings: {}".format(list(scenario.buildings.keys())))
    print("==================")

    for building_id, building in scenario.buildings.items():
        print("Building ID: {}".format(building_id))
        print("{} assets: {}".format(
            building_id,
            list(building.end_uses["stove"].keys()))
        )
        print("------------------")

    print("==================")

    print("********Utility network********")
    print("Gas meter 1 energy use: {}".format(scenario.utility_network.gas_meters[0].total_annual_energy_use))
    print("Elec meter 1 energy use: {}".format(scenario.utility_network.elec_meters[0].total_annual_energy_use))
    print("Gas meter 1 peak use: {}".format(scenario.utility_network.gas_meters[0].total_annual_peak_use))
    print("Elec meter 1 peak use: {}".format(scenario.utility_network.elec_meters[0].total_annual_peak_use))
    print("------------------")
    print("Gas meter 2 energy use: {}".format(scenario.utility_network.gas_meters[1].total_annual_energy_use))
    print("Elec meter 2 energy use: {}".format(scenario.utility_network.elec_meters[1].total_annual_energy_use))
    print("Gas meter 2 peak use: {}".format(scenario.utility_network.gas_meters[1].total_annual_peak_use))
    print("Elec meter 2 peak use: {}".format(scenario.utility_network.elec_meters[1].total_annual_peak_use))

if __name__ == "__main__":
    main()
