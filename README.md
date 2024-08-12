# Segment Intervention Analysis Tool
The Segment Intervention Analysis Tool (segment-iat) is a model for simulating energy intervention scenarios along a given street segment. The user provides a number of configuration files describing the makeup, energy consumption, and assumed intervention costs along a street. The tool then executes a given intervention scenario and reports annual indicators including total system costs, peak energy consumption, and emissions, among others.

## About the tool
segment-iat is a local energy asset planning (LEAP) simulation tool. Interventions at individual buildings are aggregated "up" the network to account for total cost and energy consumption, at times triggering upstream interventions. For example, this can occur when all gas-consuming building assets are shutoff, triggering a shutoff of the gas service line to that building. The tool outputs a number of indicators that quantify how different interventions strategies impact costs, energy consumption patterns, and emissions.

## Running the tool
The tool is executed via `run.py`. The user specifies which scenario(s) to run by providing the scenario IDs. These IDs should match the filename of the scenario settings file in `config_files/scenarios`. The script expects that the user has created all input files for the scenarios provided. The tool will display status updates to the user as the simulation is running.

The user can also provide a flag to `run.py` to perform post-processing on the results (`--postprocessing`). This will combine output tables across scenarios for easier investigation and save them to `results/{SEGMENT_NAME}`. Alternatively, the user can perform post-processing via the `postprocessing.py` script. Postprocessing must be performed in order to track the results in version control. **Model outputs saved to `outputs/` are not tracked!**

### Example
Suppose you want to run 3 different scenarios on a street segment (say, "continued_gas", "accelerated_elec", and "hybrid_npa") and combine the results from each simulation. We'll call the street segment "anytown_usa". Therefore, our scenario files are "anytown_usa_continued_gas.json", "anytown_usa_accelerated_elec.json", and "anytown_usa_hybrid_npa.json". Create these scenario files and then execute the following:
```python
python run.py anytown_usa_continued_gas anytown_usa_accelerated_elec anytown_usa_hybrid_npa --postprocessing
```

For more information on `run.py` and the input values, execute `python run.py --help`.

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

The outputs are written with the file heirarchy of `outputs/`, followed by the street segment name, followed by the scenario name for that street segment. Therefore, in the example given above, you would have the following file structure once complete:
```
outputs/
|
|---anytown_usa/
|   |
|   |---continued_gas/
|   |   |
|   |   |---book_value.csv
...
|   |---accelerated_elec/
|   |   |
|   |   |---book_value.csv
...
|   |---hybrid_npa/
|   |   |
|   |   |---book_value.csv
...
```

## Development
The tool is developed in Python. Development and execution of the tool require an environment with Python >= 3.9 and the packages described in `requirements.txt`. The environment can be created using `pip` and `virtualenv`.
