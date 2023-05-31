"""
Pre-processing checks
"""
import json
import os

import pandas as pd


BUILDING_CONFIG = "./config_files/history/doer_sf_baseline.json"
GAS_METER_CONFIG = "./config_files/GIS/SF/Gas_Meter.csv"


def check_gas_meters(buildings: list, gas_meters: pd.DataFrame):
    issues = 0

    for i in buildings:
        building_id = i["building_id"]
        fuel_type = i["original_fuel_type"]
        if building_id not in gas_meters["LOC_ID"].to_list() and fuel_type=="natural_gas":
            print(f"Building ID {i} not found in gas meters!")
            issues += 1

    for i in gas_meters["LOC_ID"].to_list():
        if i not in buildings:
            print(f"Parcel ID {i} found in gas meters config but not in building config!")
            issues += 1

    if not issues:
        print("No issues detected with gas meter inputs")


def main():
    with open(BUILDING_CONFIG) as f:
        buildings = json.load(f)

    gas_meters = pd.read_csv(GAS_METER_CONFIG)

    check_gas_meters(buildings, gas_meters)


if __name__ == "__main__":
    main()
