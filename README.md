# Tactical Thermal Transition
This repo contains scripts and database prototyping for the Tactical Thermal Transition (TTT) team

## Scenario Creator
The main function of this repository is to create input data for simulation scenarios. An example of this process can be found in the script `example.py`. The example script makes use of a set of JSON config files that are not tracked by git. See the tests for examples of config file formatting.

**_TODO: Document config file format_**

## Repo structure
### `scenario_creator/`
Contains the main entry point for creating input data, `create_scenario.py`.

### `end_uses/`
Contains classes that define different end uses in a parcel. These include appliances such as stoves and HVAC equipment.

### `parcel_database/`
This repo is the parcel database. It contains directories of parcel data and prototyping scripts. Additionally, it contains a handful of top-level python files of note:
* `example.py` - An example file for the final JSON structure of the parcel database
* `helper_funcs.py` - A file of helper functions used in prototyping notebooks
* `parcel_database_creation.py` - The main file for creating the enriched parcel database

The sub-folders of `parcel_database/` are described below.

#### `parcel_database/data_explore`
This repo contains scripts and files for exploration of the data. It is only meant for prototyping. See `parcel_database/data_explore/README.md` for more.

#### `parcel_database/database`
The core database. Raw input files are saved here, along with scripts for creating "enriched" datasets.

The directory also has files for mapping certain data to higher-level classifications. Additionally, shape files can be found here, which are spatially joined with the parcel data.

### `resstock_explore/`
Ignore for now - this directory has explorations of ResStock energy usage data
