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

        for end_use_id, end_use in building.end_uses["stove"].items():
            print("{} install cost: {}".format(end_use_id, end_use.install_cost))
            print("{} depreciation: {}".format(end_use_id, end_use.depreciation))
            print("{} stranded_value: {}".format(end_use_id, end_use.stranded_value))

        print("{} total end use install cost: {}".format(building_id, building.aggregate()))

        print("------------------")

    print("==================")

    print("********Utility network********")
    print("Gas meter 1 energy use: {}".format(scenario.utility_network.gas_meters[0].total_energy_use))
    print("Elec meter 1 energy use: {}".format(scenario.utility_network.elec_meters[0].total_energy_use))

if __name__ == "__main__":
    main()
