"""
Object for simulating a single building, accounting for energy, emissions, and costs
"""
import os
from typing import Dict, List

import numpy as np
import pandas as pd

from segment_iat.end_uses.building_end_uses.clothes_dryer import ClothesDryer
from segment_iat.end_uses.building_end_uses.domestic_hot_water import DHW
from segment_iat.end_uses.building_end_uses.hvac import HVAC
from segment_iat.end_uses.building_end_uses.stove import Stove


METHANE_LEAKS = {
    "GAS": 2,
    "HPL": 1,
}


#TODO: Make configurable for different geographies
EMISSION_FACTORS = { # tCO2 / kWh
    # Should be metric tons rather than imperial...
    "natural_gas": (53 / (293 * 907)), # Input of kgCO2 / MMBtu
    "electricity": 0.45 / 1000, # Input of tCO2 / MWh
    "fuel_oil": (73.96 / (293 * 907)), # Input of kgCO2 / MMBtu
    "propane": (61.71 / (293 * 907)), # Input of kgCO2 / MMBtu
    "hybrid_gas": (53 / (293 * 907)), # Same as natural_gas
    "hybrid_npa": (61.71 / (293 * 907)), # Same as propane
}


FUELS = [
    "electricity",
    "natural_gas",
    "propane",
    "fuel_oil",
    "thermal_cooling",
    "thermal_heating"
]


DB_BASEPATH = "./config_files/"


class Building:
    """
    A bucket for all end uses at a parcel. Currently assuming one building per parcel

    Args:
        building_params (dict): Dict of input parameters for the building
        {
            building_id (str): The building/parcel ID
            baseline_consumption_id (str): The ID of the building's baseline consumption profile
            retrofit_consumption_id (str): The ID of the building's retrofit consumption profile
            load_scaling_factor (float): The load scaling factor for the consumption
            asset_install_year (int): The install year of existing building measures
            asset_replacement_year (int): The install year of new building measures
            heating_fuel (str): The existing heating fuel for the building
            retrofit_heating_fuel (str): The heating fuel post-retrofit of the building
        }
        sim_settings (dict): Dict of simulation settings
        {
            segment_id (str): The ID of the segment
            sim_start_year (int): Start year of the study
            sim_end_year (int): End year of the study (exclusive)
            sim_name (str): The study name
            existing_appliance_costs_id (str): ID of the costs for existing building measures
            retrofit_appliance_costs_id (str): ID of the costs for new building measures
        }

    Attributes:
        building_params (dict): Dict of input parameters for the building
        years_vec (List[int]): List of simulation years
        building_id (str): The building ID, also referred to as parcel ID
        retrofit_scenario (str): The energy intervention scenario
        end_uses (dict): Dict of building asset objects, organized by asset type
        baseline_consumption (pd.DataFrame): Baseline energy consumption timeseries for the building
        retrofit_consumption (pd.DataFrame): Retrofit energy consumption timeseries for the buliding

    Methods:
        populate_building (None): Executes downstream calculations for the building simulation
        calc_building_utility_costs (Dict[str, List[float]]): Returns dict of annual consumption costs by energy source
        write_building_cost_info (None): Write building cost information to a CSV
        write_building_energy_info (None): Write building energy timeseries to a CSV
    """
    def __init__(
            self,
            building_params: dict,
            sim_settings: dict,
    ):
        self.building_params: dict = building_params
        self._sim_settings: dict = sim_settings

        self._config_filepath: str = ""
        self._year_timestamps: pd.DatetimeIndex = None
        self.years_vec: List[int] = []
        self.building_id: str = ""
        self.retrofit_scenario: str = ""
        self.end_uses: dict = {}
        self.baseline_consumption: pd.DataFrame = pd.DataFrame()
        self.retrofit_consumption: pd.DataFrame = pd.DataFrame()
        self._retrofit_vec: List[bool] = []
        self._is_retrofit_vec: List[bool] = []
        self._annual_energy_by_fuel: Dict[str, List[float]] = {}
        self._building_annual_costs_other: List[float] = []
        self._fuel_type: List[str] = []
        self._combustion_emissions: Dict[str, List[float]] = {}

    def populate_building(self) -> None:
        """
        Executes all necessary functions and calculations for simulating the building scenario

        Args:
            None

        Returns:
            None
        """
        self._config_filepath = self._set_config_filepath()
        self._get_years_vec()
        self._get_building_id()
        self.retrofit_scenario = self._get_retrofit_scenario()
        self._get_building_energies()
        self.end_uses = self._create_end_uses()
        self._calc_total_energy_baseline()
        self._calc_total_energy_retrofit()
        self._retrofit_vec = self._get_replacement_vec()
        self._is_retrofit_vec = self._get_is_retrofit_vec()
        self._annual_energy_by_fuel = self._calc_annual_energy_consump()
        #FIXME: Is this being used...?
        self._building_annual_costs_other = self._calc_building_costs()
        self._fuel_type = self._get_fuel_type_vec()
        self._methane_leaks = self._get_methane_leaks()
        self._combustion_emissions = self._get_combustion_emissions()

    def _set_config_filepath(self) -> None:
        """
        Set the _config_filepath attribute
        """
        return os.path.join(DB_BASEPATH, self._sim_settings.get("segment_id"))

    def _get_years_vec(self) -> None:
        """
        Vector of simulation years
        """
        self.years_vec = list(range(
            self._sim_settings.get("sim_start_year", 2020),
            self._sim_settings.get("sim_end_year", 2050)
        ))

        self._year_timestamps = pd.date_range(
            start="2018-01-01", end="2019-01-01", freq="h", inclusive="left"
        )

    def _get_building_id(self) -> None:
        self.building_id = self.building_params.get("building_id")

    def _get_retrofit_scenario(self) -> str:
        return self._sim_settings.get("sim_name")

    def _get_building_energies(self) -> None:
        reference_consump_id = self.building_params.get("baseline_consumption_id")
        retrofit_consump_id = self.building_params.get("retrofit_consumption_id")

        self.baseline_consumption = self._load_energy_timeseries(reference_consump_id)
        self.retrofit_consumption = self._load_energy_timeseries(retrofit_consump_id)

        load_scaling_factor = self.building_params.get("load_scaling_factor", 1)
        self.baseline_consumption[
            self.baseline_consumption.select_dtypes(include=["number"]).columns
        ]  *= load_scaling_factor

        self.retrofit_consumption[
            self.retrofit_consumption.select_dtypes(include=["number"]).columns
        ] *= load_scaling_factor

    @staticmethod
    def _load_energy_timeseries(consumption_id: str) -> pd.DataFrame:
        consump_filepath = os.path.join(DB_BASEPATH, "energy_consumption", consumption_id+".csv")
        consump_df = pd.read_csv(consump_filepath).set_index("timestamp")
        consump_df.index = pd.to_datetime(consump_df.index)

        return consump_df

    def _create_end_uses(self) -> dict:
        """
        Create the end uses for the building
        """
        end_use_instances = {}

        cost_original_filepath = os.path.join(
            self._config_filepath,
            "parcels",
            f"{self.building_params["existing_measures_cost_id"]}.csv"
        )

        cost_retrofit_filepath = os.path.join(
            self._config_filepath,
            "parcels",
            f"{self.building_params["retrofit_measures_cost_id"]}.csv"
        )

        costs_original = pd.read_csv(
            cost_original_filepath,
            index_col="parcel_id"
        ).to_dict(orient="index")

        costs_retrofit = pd.read_csv(
            cost_retrofit_filepath,
            index_col="parcel_id"
        ).to_dict(orient="index")

        building_costs_original = costs_original.get(self.building_id, {})
        building_costs_retrofit = costs_retrofit.get(self.building_id, {})

        end_uses = [
            "stove", "hvac", "clothes_dryer", "domestic_hot_water"
        ]

        for end_use in end_uses:
            individual_params = {}
            individual_params["end_use"] = end_use
            individual_params["existing_install_cost"] = building_costs_original.get(end_use)
            individual_params["replacement_cost"] = building_costs_retrofit.get(end_use)
            individual_params["existing_install_year"] = self.building_params.get("asset_install_year")
            individual_params["replacement_year"] = self.building_params.get("asset_replacement_year")
            end_use_instances[end_use] = self._get_single_end_use(individual_params)

        return end_use_instances

    def _get_single_end_use(self, params: dict):
        if params.get("end_use") == "stove":
            stove = Stove(
                self.years_vec,
                custom_baseline_energy=self.baseline_consumption,
                custom_retrofit_energy=self.retrofit_consumption,
                **params
            )

            stove.initialize_end_use()

            return stove
        
        if params.get("end_use") == "clothes_dryer":
            dryer = ClothesDryer(
                self.years_vec,
                custom_baseline_energy=self.baseline_consumption,
                custom_retrofit_energy=self.retrofit_consumption,
                **params,
            )

            dryer.initialize_end_use()

            return dryer
        
        if params.get("end_use") == "domestic_hot_water":
            dhw = DHW(
                self.years_vec,
                custom_baseline_energy=self.baseline_consumption,
                custom_retrofit_energy=self.retrofit_consumption,
                **params
            )

            dhw.initialize_end_use()

            return dhw

        if params.get("end_use") == "hvac":
            hvac = HVAC(
                self.years_vec,
                custom_baseline_energy=self.baseline_consumption,
                custom_retrofit_energy=self.retrofit_consumption,
                **params
            )

            hvac.initialize_end_use()

            return hvac

        return None

    def _calc_total_energy_baseline(self) -> None:
        """
        Calculate the total baseline consumption for the building. Contains logic for direct
        connection to ResStock or overwrite using locally-provided energy consumption profiles
        """
        for fuel in FUELS:
            filter_cols = [
                col
                for col in self.baseline_consumption
                if col.startswith("out.{}".format(fuel))
            ]

            self.baseline_consumption["out.{}.total.energy_consumption".format(fuel)] = \
                self.baseline_consumption[filter_cols].sum(axis=1)
            
        self.baseline_consumption["out.total.energy_consumption"] = self.baseline_consumption[[
            "out.{}.total.energy_consumption".format(i)
            for i in FUELS
        ]].sum(axis=1)
    
    def _calc_total_energy_retrofit(self) -> None:
        for fuel in FUELS:
            filter_cols = [
                col
                for col in self.retrofit_consumption
                if col.startswith("out.{}".format(fuel))
            ]

            self.retrofit_consumption["out.{}.total.energy_consumption".format(fuel)] = \
                self.retrofit_consumption[filter_cols].sum(axis=1)
            
        self.retrofit_consumption["out.total.energy_consumption"] = self.retrofit_consumption[[
            "out.{}.total.energy_consumption".format(i)
            for i in FUELS
        ]].sum(axis=1)
 
    def _calc_building_costs(self) -> List[float]:
        """
        Calculate building-level costs
        """
        other_assets = ["weatherization", "panel_upgrade"]

        cost_original_filepath = os.path.join(
            self._config_filepath,
            "parcels",
            f"{self.building_params["existing_measures_cost_id"]}.csv"
        )

        cost_retrofit_filepath = os.path.join(
            self._config_filepath,
            "parcels",
            f"{self.building_params["retrofit_measures_cost_id"]}.csv"
        )

        costs_original = pd.read_csv(
            cost_original_filepath,
            index_col="parcel_id"
        ).to_dict(orient="index")

        costs_retrofit = pd.read_csv(
            cost_retrofit_filepath,
            index_col="parcel_id"
        ).to_dict(orient="index")

        building_costs_original = costs_original.get(self.building_id, {})
        building_costs_retrofit = costs_retrofit.get(self.building_id, {})

        other_retrofit_cost = 0
        for asset in other_assets:
            other_retrofit_cost += building_costs_retrofit.get(asset)

        return np.multiply(other_retrofit_cost, self._retrofit_vec).tolist()

    def _get_replacement_vec(self) -> List[bool]:
        """
        The replacement vector is a vector of True when the index is the retrofit year, False o/w
        """
        replacement_year = self.building_params.get("asset_replacement_year", self.years_vec[-1])
        return [True if i==replacement_year else False for i in self.years_vec]
    
    def _get_is_retrofit_vec(self) -> List[bool]:
        """
        Derived from the retrofit vec; =True in years including and after the retrofit, 0 o/w
        """
        return [max(self._retrofit_vec[:i]) for i in range(1, len(self._retrofit_vec) + 1)]
    
    def _calc_annual_energy_consump(self) -> Dict[str, List[float]]:
        """
        Calculate the total annual energy consumption, by energy type
        """
        annual_energy_use = {i: [] for i in FUELS}

        for fuel in FUELS:
            for replaced in self._is_retrofit_vec:
                if replaced:
                    annual_use = self.retrofit_consumption[
                        "out.{}.total.energy_consumption".format(fuel)
                    ]

                else:
                    annual_use = self.baseline_consumption[
                        "out.{}.total.energy_consumption".format(fuel)
                    ]

                annual_use = annual_use.resample("YS").sum().values[0]
                annual_energy_use[fuel].append(annual_use)

        return annual_energy_use

    def _calc_building_utility_costs(self) -> Dict[str, List[float]]:
        """
        Calculate the utility billing metrics for the building, based on total energy consumption
        """
        segment_id = self._sim_settings.get("segment_id")
        energy_consump_cost_filepath = os.path.join(
            DB_BASEPATH,
            segment_id,
            "utility_network",
            f"{segment_id}_consumption_rates.csv"
        )
        consump_rates = pd.read_csv(energy_consump_cost_filepath, index_col=0)

        annual_utility_costs = {i: [] for i in FUELS}

        for fuel in FUELS:
            for replaced, rate in zip(self._is_retrofit_vec, consump_rates[fuel].to_list()):
                if replaced:
                    annual_use = self.retrofit_consumption[
                        "out.{}.total.energy_consumption".format(fuel)
                    ]

                else:
                    annual_use = self.baseline_consumption[
                        "out.{}.total.energy_consumption".format(fuel)
                    ]

                annual_use = annual_use.resample("YS").sum().values[0]

                annual_utility_costs[fuel].append(annual_use * rate)

        return annual_utility_costs
    
    def _get_fuel_type_vec(self) -> List[str]:
        """
        Fuel type vector of dominant fuel in building. Based on inputs original_fuel_type and
        retrofit_fuel_type
        """
        #TODO: There should be a heirarchy to this, based on the fuel of each asset, to determine these variables
        # OR, we should be more explicit and just call this the heating fuel... as long as that translates
        # properly to the fuel type of the other appliances
        original_fuel = self.building_params.get("heating_fuel", "")
        original_fuel = original_fuel.lower().replace(" ", "_")
        retrofit_fuel = self.building_params.get("retrofit_heating_fuel", "")
        retrofit_fuel = retrofit_fuel.lower().replace(" ", "_")

        fuel_mappings = {
            "natural_gas": "GAS",
            "fuel_oil": "OIL",
            "electricity": "ELEC",
            "propane": "LPG",
            "hybrid_gas": "HPL",
            "hybrid_npa": "NPH",
            "thermal": "TEN",
        }

        return [
            fuel_mappings.get(retrofit_fuel) if i
            else fuel_mappings.get(original_fuel)
            for i in self._is_retrofit_vec
        ]

    def _get_methane_leaks(self) -> List[str]:
        """
        Get (hardcoded) methane leaks in the building annually
        """
        return [
            METHANE_LEAKS.get(i, 0)
            for i in self._fuel_type
        ]
    
    def _get_combustion_emissions(self) -> List[str]:
        """
        Combustion emissions from energy consumption
        """
        combusion_emissions = {}

        for fuel in FUELS:
            annual_fuel_consump = self._annual_energy_by_fuel[fuel]
            emissions_factor = EMISSION_FACTORS.get(fuel, 0)

            #TODO: Make configurable
            if fuel == "electricity":
                emissions_factor = np.zeros(len(self.years_vec))
                for i in range(len(self.years_vec)):
                    year = self.years_vec[i]
                    if year < 2024:
                        emissions_factor[i] = EMISSION_FACTORS.get(fuel, 0)

                    else:
                        emissions_factor[i] = emissions_factor[i-1] * (1 - 0.03)

            combusion_emissions[fuel] = (
                np.array(annual_fuel_consump)
                * emissions_factor
            ).tolist()

        return combusion_emissions

    def write_building_energy_info(self, freq: int =60) -> None:
        """
        Write building energy timeseries (baseline and retrofit) to output CSV

        Args:
            None

        Optional Args:
            freq (int): The frequency of the timeseries output in minutes

        Returns:
            None
        """
        if freq < 15:
            print("Unable to resample to under 15 minutes!")
            print("Outputting in 15 minute frequency...")
            freq = 15

        resample_string = "{}T".format(freq)

        self.baseline_consumption.resample(resample_string).sum(axis=0).to_csv(
            "./outputs/{}_baseline_consump.csv".format(self.building_id)
        )

        self.retrofit_consumption.resample(resample_string).sum(axis=0).to_csv(
            "./outputs/{}_retrofit_consump.csv".format(self.building_id)
        )

    def write_building_cost_info(self) -> None:
        """
        Write calculated building information for total costs to output CSV

        Args:
            None

        Returns:
            None
        """
        cost_table = pd.DataFrame(index=self.years_vec)

        cost_table["building_other_costs"] = self._building_annual_costs_other

        for asset_type in ["stove", "clothes_dryer", "domestic_hot_water", "hvac"]:
            asset = self.end_uses.get(asset_type)

            if asset:
                cost_table = pd.concat([cost_table, asset.cost_table], axis=1)

        cost_table.to_csv("./outputs/{}_costs.csv".format(self.building_id))

    def _get_retrofit_cost_vec(self) -> List[float]:
        """
        Sum replacement_cost vec from each asset to get total
        """
        replacement_costs = pd.DataFrame(index=self.years_vec)

        for asset_type in ["stove", "clothes_dryer", "domestic_hot_water", "hvac"]:
            asset = self.end_uses.get(asset_type)

            if asset:
                replacement_cost = asset.replacement_cost
                replacement_costs[asset_type] = replacement_cost

        return replacement_costs.sum(axis=1).to_list()
    
    def _get_retrofit_book_value_vec(self) -> List[float]:
        """
        Sum replacement_book_val vec
        """
        replacement_costs = pd.DataFrame(index=self.years_vec)

        for asset_type in ["stove", "clothes_dryer", "domestic_hot_water", "hvac"]:
            asset = self.end_uses.get(asset_type)

            if asset:
                replacement_cost = asset.replacement_book_val
                replacement_costs[asset_type] = replacement_cost

        return replacement_costs.sum(axis=1).to_list()
    
    def _get_exising_book_val_vec(self) -> List[float]:
        existing_book_val = pd.DataFrame(index=self.years_vec)

        for asset_type in ["stove", "clothes_dryer", "domestic_hot_water", "hvac"]:
            asset = self.end_uses.get(asset_type)

            if asset:
                book_val = asset.existing_book_val
                existing_book_val[asset_type] = book_val

        return existing_book_val.sum(axis=1).to_list()
    
    def _get_exising_stranded_val_vec(self) -> List[float]:
        existing_stranded = pd.DataFrame(index=self.years_vec)

        for asset_type in ["stove", "clothes_dryer", "domestic_hot_water", "hvac"]:
            asset = self.end_uses.get(asset_type)

            if asset:
                book_val = asset.existing_stranded_val
                existing_stranded[asset_type] = book_val

        return existing_stranded.sum(axis=1).to_list()
