# Tactical Thermal Transition
The Tactical Thermal Transition (TTT) tool is a model for simulating energy intervention scenarios along a given street segment. The user provides a number of configuration files describing the makeup, energy consumption, and assumed intervention costs along a street. The tool then executes a given intervention scenario and reports annual indicators including total system costs, peak energy consumption, and emissions, among others.

## About the tool
The TTT tool is a local energy asset planning (LEAP) simulation tool. Interventions at individual buildings are aggregated "up" the network to account for total cost and energy consumption, at times triggering upstream interventions. For example, this can occur when all gas-consuming building assets are shutoff, triggering a shutoff of the gas service line to that building. The tool outputs a number of indicators that quantify how different interventions strategies impact costs, energy consumption patterns, and emissions.

## Running the tool
The tool is executed via `run.py`. This script expects that the user has created all input files for the following scenario:
* "continued_gas"
* "accelerated_elec"
* "accelerated_elec_higheff"
* "natural_elec"
* "natural_elec_higheff"
* "hybrid_gas"
* "hybrid_gas_immediate"
* "hybrid_npa"

The user must specify which street segment to run. The tool currently assumes the user is executing the DOER scenarios. Therefore, executing `run.py` with `street_segment` set to `mf` will run all DOER multifamily scenarios. The user must edit the `run.py` file to run other street segments.

Once all configuration files are created, the user can enter `python run.py` in a terminal to execute the tool. The tool will display status updates to the user as the simulation is running.

Once all scenarios are run, outputs can be combined via `python postprocessing.py`. This will combine output tables across scenarios for easier investigation and save them to `outputs_combined/scenario/combined`.

### Outputs
All output tables are written to CSVs, which can be utilized for further investigation. The output tables are as follows:
* `book_value`: The annual depreciated book value of all assets over the simulation timeframe.
* `consumption_costs`: The cost to an individual consumer for their energy consumption. This is organized by energy source (electricity, natural gas, etc).
* `consumption_emissions`: The carbon emissions associated with energy consumption. Note that these are different from leak emissions.
* `energy_consumption`: The total annual energy consumption, by energy source, of an entity.
* `fuel_type`: The dominant fuel type each year at a building
* `is_retrofit_vec_table`: This annual vector is `True` in the retrofit year and all subsequent years. It helps indicate whether or not a given entity has been retrofit.
* `methan_leaks`: The annual methane leaks in the system, organized by various entities (total leaks within the building, leaks within a given pipe, etc).
* `operating_costs`: The annual operating associated with an entity. Currently, this only outputs operating costs for gas utility assets.
* `peak_consump`: The annual peak consumption at electric transformers based on downstream energy consumption at connected buildings.
* `retrofit_cost`: The annual cost of retrofitting an asset.
* `retrofit_year`: Similar to the `is_retrofit_vec_table`, except this vector is only `True` in the asset's retrofit year.
* `stranded_val`: The stranded value of an asset in a given year if it is retrofit prior to the end of its useful life (before it fully depreciates).

## Development
The tool is developed in Python. Development and execution of the tool require an environment with Python >= 3.9 and the packages described in `requirements.txt`. The environment can be created using `pip` and `virtualenv`.
