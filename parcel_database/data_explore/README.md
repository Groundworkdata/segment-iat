# Data Explore
This repo contains all scripts and files for prototyping of features with the parcel database.

## `parcel_data`
Contains `.json` and `.csv` files of example parcel databases

## `spatial`
Contains example spatial data and scripts merging spatial and parcel data

## `utility_sim`
Prototypes scripts to seed the UtilitySim model. The main script for this is `model_inputs_generator.py`. This script reads in JSON parcel database and, based on inputs from `kitchen_retrofit_seed.csv`, generates model inputs for kitchen gas stove replacement. `kitchen_retrofit_seed.csv` is intended as a set of user inputs for year of kitchen appliance replacement, organized by parcel ID.
