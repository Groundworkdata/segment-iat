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

## Energy modeling
The tool currently expects energy consumption timeseries profiles provided for an entire year, with timestamps as time-beginning. The energy data is handled as if it has come from ResStock, with some pre-processing. One necessary pre-processing step for ResStock is to shift all timestamps one period *back* so they are time-beginning (ResStock uses time-ending). The tool tracks energy consumption from four different fuels: electricity, natural gas, propane, and fuel oil. The tool also calculates total energy consumption for the entire building. It is expected that all consumption data is provided in kWh.

Energy consumption can be provided one of two ways:
1. Energy consumption is provided by end use and *does not* include total energy consumption. Total energy consumption is calculated by the tool and including total energy consumption will lead to double counting. This is true both for total building energy consumption and total energy consumption by fuel.
2. Only total energy consumption by fuel type is provided. Total energy consumption for the building is still calculated as in (1). This is the lower-effort way to set up a new scenario; just pull the desired profiles from ResStock and only keep the following columns: `out.electricity.total.energy_consumption`, `out.natural_gas.total.energy_consumption`, `out.propane.total.energy_consumption`, `out.fuel_oil.total.energy_consumption`.

The original intention was to track energy consumption by end use (HVAC, DHW, clothes dryer, stove), but this is not fully developed at this time. The purpose was to implement advanced logic for energy modeling that is not available in ResStock (for example, converting gas cooking to propane cooking for customers that do not want to ditch "flame" cooking).

Tracking energy consumption by end use will require the following keys in the energy profile (in development). This is inspired by ResStock:
```python
# HVAC
"out.electricity.heating.energy_consumption"
"out.electricity.heating_hp_bkup.energy_consumption"
"out.electricity.cooling.energy_consumption"
"out.natural_gas.heating.energy_consumption"
"out.natural_gas.heating_hp_bkup.energy_consumption"
"out.propane.heating.energy_consumption"
"out.propane.heating_hp_bkup.energy_consumption"
"out.fuel_oil.heating.energy_consumption"
"out.fuel_oil.heating_hp_bkup.energy_consumption"
# Domestic hot water
"out.electricity.hot_water.energy_consumption"
"out.natural_gas.hot_water.energy_consumption"
"out.propane.hot_water.energy_consumption"
"out.fuel_oil.hot_water.energy_consumption"
# Clothes dryer
"out.electricity.clothes_dryer.energy_consumption"
"out.natural_gas.clothes_dryer.energy_consumption"
"out.propane.clothes_dryer.energy_consumption"
# Stove
"out.electricity.range_oven.energy_consumption"
"out.natural_gas.range_oven.energy_consumption"
"out.propane.range_oven.energy_consumption"
# Other
"out.electricity.other.energy_consumption"
"out.natural_gas.other.energy_consumption"
"out.propane.other.energy_consumption"
"out.fuel_oil.other.energy_consumption"
```

Note that energy consumption profiles are purposefully not tracked in git because of their size (they are 8760 rows or larger, times multiple columns). The intention in the future is to not track any model inputs in this repo and instead track those in a separate version controlled environment (a separate Github repo or other location).

## Example Study
`segment-iat` comes with an example Study named `example_street`. This Study analyzes a hypothetical pipe segment in Westchester County, NY, that serves 20 single family homes from 2025 to 2050. The homes are all of similar square footage, vintage, and materials. The exact building IDs queried from ResStock for this example Study are 16133, 45920, 49049, and 68538. The example Scenarios for the Study are as follows:
* `ex_gas`: All homes stay on gas and the pipe is replaced in 2025 (ResStock Measure Package Baseline)
* `ex_managed_elec_1`: All homes electrify w/ ENERGY STAR ASHP and the pipe is decommissioned in 2025 (ResStock Measure Package 11)
* `ex_managed_elec_2`: All homes electrify w/ maximum efficiency ASHP and the pipe is decommissioned in 2025 (ResStock Measure Package 13)
* `ex_managed_gshp`: All homes electrify w/ a GSHP as defined in ResStock and the pipe is decommissioned in 2025 (ResStock Measure Package 15)

Cost data for the `example_street` Study come from multiple sources, including electrification cost estimates from Rewiring America and MassCEC whole-home pilot data.

## Development
The tool is developed in Python. Development and execution of the tool require an environment with Python >= 3.9 and the packages described in `requirements.txt`.
