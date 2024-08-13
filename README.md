# Segment Intervention Analysis Tool
The Segment Intervention Analysis Tool (`segment-iat`) is a model for simulating intervention scenarios for a given segment of gas distribution pipe. The user provides a number of configuration files describing the makeup, energy consumption, and assumed intervention costs along the pipe. The tool then executes given intervention scenarios and reports annual indicators including total system costs, peak energy consumption, and emissions, among others. This tool enables an expanded cost-benefit analysis for the future of gas with a hyper-local focus on specific segments of the distribution system.

## About the tool
`segment-iat` is a local energy asset planning (LEAP) simulation tool. Interventions at individual buildings are aggregated "up" the network to determine upstream impacts (i.e. the impact of electrification on the local electric grid) and quantify summary values (i.e. total capital investment in buildings). The tool outputs a number of indicators that quantify how different intervention strategies impact costs, energy consumption patterns, and emissions.

Simulations are organized by **Study**, where each Study is comprised of multiple **Scenarios**. Each Scenario in a Study varies the interventions made at individual buildings (ex: which heat pump to install) and the utility network (ex: when to replace the gas distribution main).

## Running the tool
The tool is executed via `run.py`. The user specifies a Study to run by providing the Study ID. The ID should match the directory name of the Study in `config_files/`. The script expects that the user has created all input files for the Study and the Study's Scenarios. The tool will display status updates to the user as the Study is running.

To run the example_street Study:
```python
python run.py example_street
```

The user can also choose to run a subset of Scenarios for a given Study using the `--scenario` flag, followed by the Scenario ID(s). 

To run only a subset of Scenarios for a given Study:
```python
python run.py example_street --scenario ex_managed_elec_1 ex_gas
```

By default, outputs are saved per Scenario to the `outputs/` directory. Alternatively, outputs can be combined across Scenarios for a given Study via the `--postprocessing` flag. This concatentates similar tables from multiple Scenarios into one table and saves the result in the `results/` directory.

```python
python run.py example_street --postprocessing
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

The outputs are written to the `outputs/` directory, organized by Study ID, then Scenario ID.
```
outputs/
|
|---example_street/
|   |
|   |---ex_gas/
|   |   |
|   |   |---book_value.csv
...
|   |---ex_managed_elec_1/
|   |   |
|   |   |---book_value.csv
...
```

## Development
The tool is developed in Python. Development and execution of the tool require an environment with Python >= 3.9 and the packages described in `requirements.txt`.
