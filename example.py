"""
Example script of using the repo
"""
from scenario_creator.create_scenario import ScenarioCreator


def main():
    parcel_id = "some-id"
    install_year = 2021
    install_cost = 100
    lifetime = 10
    energy_consump = 400
    sim_start_year = 2021
    sim_end_year = 2035
    replacement_year = 2031

    scenario = ScenarioCreator(
        parcel_id,
        install_year,
        install_cost,
        lifetime,
        energy_consump,
        sim_start_year,
        sim_end_year,
        replacement_year
    )

    scenario.create_scenario()

    print(scenario.total_elec_consump)

if __name__ == "__main__":
    main()
