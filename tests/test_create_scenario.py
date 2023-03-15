import sys

sys.path.append("../")

from scenario_creator.create_scenario import ScenarioCreator

#TODO: Re-write so this runs in our testing pipeline

def main(sim_settings_file=None, utility_network_config_file=None):
    # setup scenario creators
    utility_scenario = ScenarioCreator(
        sim_settings_filepath=sim_settings_file,
        building_config_filepath=" ",
        utility_network_config_filepath=utility_network_config_file,
    )

    # create the scenario
    utility_scenario.create_scenario()

    # print(utility_scenario.sim_config)


if __name__ == "__main__":
    sim_settings_file = "../tests/input_data/sim_settings_config.json"
    utility_network_config_file = "../tests/input_data/utility_network_config.json"

    main(
        sim_settings_file=sim_settings_file,
        utility_network_config_file=utility_network_config_file,
    )
