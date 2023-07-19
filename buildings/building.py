"""
Object for simulating a single building, accounting for energy, emissions, and costs
"""
from typing import Dict, List

import numpy as np
import pandas as pd

from end_uses.building_end_uses.clothes_dryer import ClothesDryer
from end_uses.building_end_uses.domestic_hot_water import DHW
from end_uses.building_end_uses.hvac import HVAC
from end_uses.building_end_uses.stove import Stove


ASSET_ENERGY_CONSUMP_KEYS = [
    # stove
    "out.electricity.range_oven.energy_consumption",
    "out.natural_gas.range_oven.energy_consumption",
    "out.propane.range_oven.energy_consumption",
    # clothes dryer
    "out.electricity.clothes_dryer.energy_consumption",
    "out.natural_gas.clothes_dryer.energy_consumption",
    "out.propane.clothes_dryer.energy_consumption",
    # DHW
    "out.electricity.hot_water.energy_consumption",
    "out.natural_gas.hot_water.energy_consumption",
    "out.propane.hot_water.energy_consumption",
    "out.fuel_oil.hot_water.energy_consumption",
    # HVAC
    "out.electricity.heating.energy_consumption",
    "out.electricity.heating_hp_bkup.energy_consumption", # hybrid configuration
    "out.electricity.cooling.energy_consumption",
    "out.natural_gas.heating.energy_consumption",
    "out.natural_gas.heating_hp_bkup.energy_consumption", # hybrid configuration
    "out.propane.heating.energy_consumption",
    "out.propane.heating_hp_bkup.energy_consumption", # hybrid configuration
    "out.fuel_oil.heating.energy_consumption",
    "out.fuel_oil.heating_hp_bkup.energy_consumption", #hybrid configuration
]


RESSTOCK_ENERGY_CONSUMP_KEYS = [
    "out.site_energy.total.energy_consumption",
    "out.electricity.total.energy_consumption",
    "out.natural_gas.total.energy_consumption",
    "out.fuel_oil.total.energy_consumption",
    "out.propane.total.energy_consumption",
    # Add assets
    *ASSET_ENERGY_CONSUMP_KEYS
]


CUSTOM_ENERGY_CONSUMP_KEYS = [
    "elec.heating",
    "elec.cooling",
    "elec.cooking",
    "elec.clothes_dryer",
    "elec.heating_backup",
    "elec.hot_water",
    "elec.other",
    "elec.ev",
    "gas.cooking",
    "gas.clothes_dryer",
    "gas.heating",
    "gas.heating_backup",
    "gas.hot_water",
    "oil.heating",
    "oil.heating_backup",
    "oil.hot_water",
    "lpg.cooking",
    "lpg.clothes_dryer",
    "lpg.heating",
    "lpg.heating_backup",
    "lpg.hot_water",
]


CUSTOM_RESSTOCK_MAPPING = {
    # elec
    'elec.clothes_dryer': 'out.electricity.clothes_dryer.energy_consumption',
    'elec.cooking': 'out.electricity.range_oven.energy_consumption',
    'elec.cooling': 'out.electricity.cooling.energy_consumption',
    'elec.heating': 'out.electricity.heating.energy_consumption',
    'elec.heating_backup': 'out.electricity.heating_hp_bkup.energy_consumption',
    'elec.hot_water': 'out.electricity.hot_water.energy_consumption',
    "elec.other": "out.electricity.other.energy_consumption",
    "elec.ev": "out.electricity.ev.energy_consumption",
    # fuel oil
    'fuel.clothes_dryer': 'out.fuel_oil.clothes_dryer.energy_consumption',
    'fuel.cooking': 'out.fuel_oil.range_oven.energy_consumpy',
    'fuel.heating': 'out.fuel_oil.heating.energy_consumption',
    'fuel.heating_backup': 'out.fuel_oil.heating_hp_bkup.energy_consumption',
    'fuel.hot_water': 'out.fuel_oil.hot_water.energy_consumption',
    'oil.heating': 'out.fuel_oil.heating.energy_consumption',
    'oil.heating_backup': 'out.fuel_oil.heating_hp_bkup.energy_consumption',
    'oil.hot_water': 'out.fuel_oil.hot_water.energy_consumption',
    # nat gas
    'gas.clothes_dryer': 'out.natural_gas.clothes_dryer.energy_consumption',
    'gas.cooking': 'out.natural_gas.range_oven.energy_consumption',
    'gas.heating': 'out.natural_gas.heating.energy_consumption',
    'gas.heating_backup': 'out.natural_gas.heating_hp_bkup.energy_consumption',
    'gas.hot_water': 'out.natural_gas.hot_water.energy_consumption',
    # propane
    'lpg.clothes_dryer': 'out.propane.clothes_dryer.energy_consumption',
    'lpg.cooking': 'out.propane.range_oven.energy_consumption',
    'lpg.heating': 'out.propane.heating.energy_consumption',
    'lpg.heating_backup': 'out.propane.heating_hp_bkup.energy_consumption',
    'lpg.hot_water': 'out.propane.hot_water.energy_consumption',
}


METHANE_LEAKS = {
    "GAS": 2,
    "HPL": 1,
}


#TODO: Make configurable for different geographies
EMISSION_FACTORS = { # tCO2 / kWh
    "natural_gas": (53 / (293 * 907)), # Input of kgCO2 / MMBtu
    "electricity": 0.45 / 1000, # Input of tCO2 / MWh
    "fuel_oil": (73.96 / (293 * 907)), # Input of kgCO2 / MMBtu
    "propane": (61.71 / (293 * 907)), # Input of kgCO2 / MMBtu
    "hybrid_gas": (53 / (293 * 907)), # Same as natural_gas
    "hybrid_npa": (61.71 / (293 * 907)), # Same as propane
}


HYBRID_NPA_SCENARIO = "hybrid_npa"


class Building:
    """
    A bucket for all end uses at a parcel. Currently assuming one building per parcel

    Args:
        building_params (dict): Dict of input parameters for the building
        sim_settings (dict): Dict of simulation settings
        scenario_mapping (List[dict]): Config for parsing data from ResStock

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
        write_building_cost_info (None): Write building cost information to a CSV
        write_building_energy_info (None): Write building energy timeseries to a CSV
    """
    def __init__(
            self,
            building_params: dict,
            sim_settings: dict,
            scenario_mapping: List[dict],
    ):
        self.building_params: dict = building_params
        self._sim_settings: dict = sim_settings
        self._scenario_mapping: List[dict] = scenario_mapping

        self._resstock_metadata = building_params.get("resstock_metadata")
        self._year_timestamps: pd.DatetimeIndex = None
        self.years_vec: List[int] = []
        self.building_id: str = ""
        self.retrofit_scenario: str = ""
        self._retrofit_params: dict = {}
        self.end_uses: dict = {}
        self._resstock_scenarios: Dict[int, pd.DataFrame] = {}
        self._main_resstock_retrofit_scenario: int = None
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
        self._get_years_vec()
        self._get_building_id()
        self.retrofit_scenario = self._get_retrofit_scenario()
        self._retrofit_params = self._get_retrofit_params()
        self._get_building_energies()
        self._create_end_uses()
        self._calc_total_energy_baseline()
        self._calc_total_energy_retrofit()
        self._retrofit_vec = self._get_replacement_vec()
        self._is_retrofit_vec = self._get_is_retrofit_vec()
        self._annual_energy_by_fuel = self._calc_annual_energy_consump()
        self._building_annual_costs_other = self._calc_building_costs()
        self._fuel_type = self._get_fuel_type_vec()
        self._methane_leaks = self._get_methane_leaks()
        self._combustion_emissions = self._get_combustion_emissions()

    def _get_years_vec(self) -> None:
        """
        Vector of simulation years
        """
        self.years_vec = list(range(
            self._sim_settings.get("sim_start_year", 2020),
            self._sim_settings.get("sim_end_year", 2050)
        ))

        self._year_timestamps = pd.date_range(
            start="2018-01-01", end="2019-01-01", freq="H", inclusive="left"
        )

    def _get_building_id(self) -> None:
        self.building_id = self.building_params.get("building_id")

    def _get_retrofit_scenario(self) -> str:
        return self._sim_settings.get("decarb_scenario")

    def _get_retrofit_params(self) -> dict:
        scenario_params = next(
            (i for i in self._scenario_mapping if i["description"]==self.retrofit_scenario),
            None
        )

        if not scenario_params:
            raise ValueError(
                "Invalid decarb scenario provided. "
                "Provided scenario '{}' not in scenario mapping".format(self.retrofit_scenario)
            )

        return scenario_params

    def _get_building_energies(self) -> None:
        if self.building_params.get("resstock_overwrite"):
            self._get_custom_building_energies()

        else:
            self._get_resstock_buildings()
            self._get_baseline_consumptions()
            self._get_retrofit_consumptions()

    def _get_custom_building_energies(self) -> None:
        reference_consump_filepath = self.building_params.get("reference_consump_filepath")
        retrofit_consump_filepath = self.building_params.get("retrofit_consump_filepath")

        self.baseline_consumption = self._load_custom_energy(reference_consump_filepath)
        self.retrofit_consumption = self._load_custom_energy(retrofit_consump_filepath)

        load_scaling_factor = self.building_params.get("load_scaling_factor", 1)
        self.baseline_consumption[
            self.baseline_consumption.select_dtypes(include=["number"]).columns
        ]  *= load_scaling_factor

        self.retrofit_consumption[
            self.retrofit_consumption.select_dtypes(include=["number"]).columns
        ] *= load_scaling_factor

    @staticmethod
    def _load_custom_energy(consump_filepath: str) -> pd.DataFrame:
        consump_df = pd.read_csv(consump_filepath).set_index("timestamp")
        consump_df.index = pd.to_datetime(consump_df.index)
        consump_df.index = consump_df.index.shift(-1, "15T")
        consump_df = consump_df.rename(mapper=CUSTOM_RESSTOCK_MAPPING, axis=1)

        return consump_df

    def _get_resstock_buildings(self) -> None:
        self._main_resstock_retrofit_scenario = self._retrofit_params.get(
            "main_resstock_retrofit_scenario"
        )

        resstock_scenarios = self._retrofit_params.get("resstock_scenarios")
        resstock_scenarios.append(0)
        resstock_scenarios = list(set(resstock_scenarios))

        for i in resstock_scenarios:
            self._resstock_scenarios[i] = self._get_resstock_scenario(i)

    def _get_resstock_scenario(self, i) -> pd.DataFrame:
        return self._resstock_timeseries_connector("MA", i, self.building_params.get("resstock_id"))
    
    def _get_baseline_consumptions(self) -> None:
        self.baseline_consumption = self._resstock_scenarios[0][RESSTOCK_ENERGY_CONSUMP_KEYS]

        for fuel in ["electricity", "natural_gas", "propane", "fuel_oil"]:
            asset_fuel_keys = [i for i in ASSET_ENERGY_CONSUMP_KEYS if fuel in i]
            asset_fuel_consumps = self.baseline_consumption[asset_fuel_keys].sum(axis=1)

            self.baseline_consumption["out.{}.other.energy_consumption".format(fuel)] = (
                self.baseline_consumption["out.{}.total.energy_consumption".format(fuel)]
                - asset_fuel_consumps
            )

    def _get_retrofit_consumptions(self) -> None:
        self.retrofit_consumption = self._resstock_scenarios[
            self._main_resstock_retrofit_scenario
        ][RESSTOCK_ENERGY_CONSUMP_KEYS]

        for fuel in ["electricity", "natural_gas", "propane", "fuel_oil"]:
            asset_fuel_keys = [i for i in ASSET_ENERGY_CONSUMP_KEYS if fuel in i]
            asset_fuel_consumps = self.retrofit_consumption[asset_fuel_keys].sum(axis=1)

            self.retrofit_consumption["out.{}.other.energy_consumption".format(fuel)] = (
                self.retrofit_consumption["out.{}.total.energy_consumption".format(fuel)]
                - asset_fuel_consumps
            )

    def _create_end_uses(self):
        """
        Create the end uses for the building
        """
        end_use_params: List[dict] = self.building_params.get("end_uses", [{}])

        #TODO: These costs should be part of asset configs rather than the current format
        cost_original_filepath = self.building_params.get("original_asset_cost_filepath")
        cost_retrofit_filepath = self.building_params.get("retrofit_asset_cost_filepath")

        costs_original = pd.read_csv(
            cost_original_filepath,
            index_col="building_id"
        ).to_dict(orient="index")

        costs_retrofit = pd.read_csv(
            cost_retrofit_filepath,
            index_col="building_id"
        ).to_dict(orient="index")

        building_costs_original = costs_original.get(self.building_id)
        building_costs_retrofit = costs_retrofit.get(self.building_id)

        for end_use in end_use_params:
            end_use_type = end_use.get("end_use")

            end_use["existing_install_cost"] = building_costs_original.get(end_use_type.upper())
            end_use["replacement_cost"] = building_costs_retrofit.get(end_use_type.upper())

            self.end_uses[end_use_type] = self._get_single_end_use(end_use)

    def _get_single_end_use(self, params: dict):
        if params.get("end_use") == "stove":
            stove = Stove(
                params.pop("original_energy_source"),
                self._resstock_scenarios,
                self._scenario_mapping,
                self.retrofit_scenario,
                self._resstock_metadata,
                self.years_vec,
                custom_baseline_energy=self.baseline_consumption,
                custom_retrofit_energy=self.retrofit_consumption,
                **params
            )

            stove.initialize_end_use()

            return stove
        
        if params.get("end_use") == "clothes_dryer":
            dryer = ClothesDryer(
                params.pop("original_energy_source"),
                self._resstock_scenarios,
                self._scenario_mapping,
                self.retrofit_scenario,
                self._resstock_metadata,
                self.years_vec,
                custom_baseline_energy=self.baseline_consumption,
                custom_retrofit_energy=self.retrofit_consumption,
                **params,
            )

            dryer.initialize_end_use()

            return dryer
        
        if params.get("end_use") == "domestic_hot_water":
            dhw = DHW(
                params.pop("original_energy_source"),
                self._resstock_scenarios,
                self._scenario_mapping,
                self.retrofit_scenario,
                self._resstock_metadata,
                self.years_vec,
                custom_baseline_energy=self.baseline_consumption,
                custom_retrofit_energy=self.retrofit_consumption,
                **params
            )

            dhw.initialize_end_use()

            return dhw
        
        if params.get("end_use") == "hvac":
            hvac = HVAC(
                params.pop("original_energy_source"),
                self._resstock_scenarios,
                self._scenario_mapping,
                self.retrofit_scenario,
                self._resstock_metadata,
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
        if self.building_params.get("resstock_overwrite"):
            self._calc_total_custom_baseline()

        else:
            self._calc_baseline_energy()

    def _calc_total_custom_baseline(self) -> None:
        """
        Calculate the baseline energy consumption using custom input energy consumption profiles
        """
        for fuel in ["electricity", "natural_gas", "propane", "fuel_oil"]:
            filter_cols = [
                col
                for col in self.baseline_consumption
                if col.startswith("out.{}".format(fuel))
            ]

            self.baseline_consumption["out.{}.total.energy_consumption".format(fuel)] = \
                self.baseline_consumption[filter_cols].sum(axis=1)
            
        self.baseline_consumption["out.total.energy_consumption"] = self.baseline_consumption[[
            "out.{}.total.energy_consumption".format(i)
            for i in ["electricity", "natural_gas", "propane", "fuel_oil"]
        ]].sum(axis=1)

    def _calc_baseline_energy(self) -> None:
        """
        Calculate the baseline energy consumption using direct connection to ResStock

        Steps:
        1. Get a single asset
        2. Get all asset energies and add them to the building consumption dataframe with underscore
            "update"
        3. Repeat 1 and 2 for all assets
        4. Get all asset consumptions ("_update") of a given energy type
        5. Get the building "other" consumption for that energy type
        6. Calculate the updated total building consumption for that energy type as the sum of 4 & 5
        7. Repeat 4-6 for all energy types
        """
        for asset_type in ["stove", "clothes_dryer", "domestic_hot_water", "hvac"]:
            if asset_type in self.end_uses:
                asset = self.end_uses.get(asset_type)

                baseline_energies_asset = asset.baseline_energy_use

                self.baseline_consumption = pd.concat(
                    [
                        self.baseline_consumption,
                        baseline_energies_asset.rename(
                            columns={
                                col: "{}_update".format(col) for col in baseline_energies_asset
                            }
                        )
                    ],
                    axis=1
                )

        asset_updates = [i for i in self.baseline_consumption.columns if i.endswith("_update")]

        for fuel in ["electricity", "natural_gas", "propane", "fuel_oil"]:
            asset_update_consump_keys = [
                i for i in asset_updates if i.startswith("out.{}".format(fuel))
            ]
            asset_update_consump_keys.append("out.{}.other.energy_consumption".format(fuel))

            self.baseline_consumption["out.{}.total.energy_consumption_update".format(fuel)] = \
                self.baseline_consumption[asset_update_consump_keys].sum(axis=1)
            
    def _calc_total_energy_retrofit(self) -> None:
        if self.building_params.get("resstock_overwrite"):
            self._calc_total_custom_retrofit()

        else:
            self._calc_retrofit_energy()

    def _calc_total_custom_retrofit(self) -> None:
        for fuel in ["electricity", "natural_gas", "propane", "fuel_oil"]:
            filter_cols = [
                col
                for col in self.retrofit_consumption
                if col.startswith("out.{}".format(fuel))
            ]

            self.retrofit_consumption["out.{}.total.energy_consumption".format(fuel)] = \
                self.retrofit_consumption[filter_cols].sum(axis=1)
            
        self.retrofit_consumption["out.total.energy_consumption"] = self.retrofit_consumption[[
            "out.{}.total.energy_consumption".format(i)
            for i in ["electricity", "natural_gas", "propane", "fuel_oil"]
        ]].sum(axis=1)

    def _calc_retrofit_energy(self) -> None:
        """
        Steps are same as _calc_baseline_energy
        """
        for asset_type in ["stove", "clothes_dryer", "domestic_hot_water", "hvac"]:
            if asset_type in self.end_uses:
                asset = self.end_uses.get(asset_type)

                retrofit_energies_stove = asset.retrofit_energy_use

                self.retrofit_consumption = pd.concat(
                    [
                        self.retrofit_consumption,
                        retrofit_energies_stove.rename(
                            columns={
                                col: "{}_update".format(col) for col in retrofit_energies_stove
                            }
                        )
                    ],
                    axis=1
                )

        asset_updates = [i for i in self.retrofit_consumption.columns if i.endswith("_update")]

        # If NPA, we need to switch all gas "other" to propane
        if self.retrofit_scenario == HYBRID_NPA_SCENARIO:
            self.retrofit_consumption.loc[:, "out.propane.other.energy_consumption"] += \
                self.retrofit_consumption.loc[:, "out.natural_gas.other.energy_consumption"]
            
            self.retrofit_consumption.loc[:, "out.natural_gas.other.energy_consumption"] = 0

        for fuel in ["electricity", "natural_gas", "propane", "fuel_oil"]:
            asset_update_consump_keys = [
                i for i in asset_updates if i.startswith("out.{}".format(fuel))
            ]
            asset_update_consump_keys.append("out.{}.other.energy_consumption".format(fuel))

            self.retrofit_consumption["out.{}.total.energy_consumption_update".format(fuel)] = \
                self.retrofit_consumption[asset_update_consump_keys].sum(axis=1)
            
    def _calc_building_costs(self) -> List[float]:
        """
        Calculate building-level costs
        """
        building_level_costs = self.building_params.get("building_level_costs", {})
        retrofit_adders = building_level_costs.get("retrofit_adder", {})
        retrofit_size = self.building_params.get("retrofit_size", "")
        retrofit_adder = retrofit_adders.get(retrofit_size.lower(), 0)

        return np.multiply(retrofit_adder, self._retrofit_vec).tolist()

    def _get_replacement_vec(self) -> List[bool]:
        """
        The replacement vector is a vector of True when the index is the retrofit year, False o/w
        """
        replacement_year = self.building_params.get("retrofit_year", self.years_vec[-1])
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
        annual_energy_use = {
            "electricity": [],
            "natural_gas": [],
            "propane": [],
            "fuel_oil": [],
        }

        for fuel in ["electricity", "natural_gas", "propane", "fuel_oil"]:
            for replaced in self._is_retrofit_vec:
                if replaced:
                    annual_use = self.retrofit_consumption[
                        "out.{}.total.energy_consumption".format(fuel)
                    ]

                else:
                    annual_use = self.baseline_consumption[
                        "out.{}.total.energy_consumption".format(fuel)
                    ]

                annual_use = annual_use.resample("AS").sum().values[0]
                annual_energy_use[fuel].append(annual_use)

        return annual_energy_use

    def _calc_building_utility_costs(self) -> Dict[str, List[float]]:
        """
        Calculate the utility billing metrics for the building, based on total energy consumption
        """
        energy_consump_cost_filepath = self.building_params.get("consump_costs_filepath")
        consump_rates = pd.read_csv(energy_consump_cost_filepath, index_col=0)

        annual_utility_costs = {
            "electricity": [],
            "natural_gas": [],
            "propane": [],
            "fuel_oil": [],
        }

        for fuel in ["electricity", "natural_gas", "propane", "fuel_oil"]:
            for replaced, rate in zip(self._is_retrofit_vec, consump_rates[fuel].to_list()):
                if replaced:
                    annual_use = self.retrofit_consumption[
                        "out.{}.total.energy_consumption".format(fuel)
                    ]

                else:
                    annual_use = self.baseline_consumption[
                        "out.{}.total.energy_consumption".format(fuel)
                    ]

                annual_use = annual_use.resample("AS").sum().values[0]

                annual_utility_costs[fuel].append(annual_use * rate)

        return annual_utility_costs
    
    def _get_fuel_type_vec(self) -> List[str]:
        """
        Fuel type vector of dominant fuel in building. Based on inputs original_fuel_type and
        retrofit_fuel_type
        """
        original_fuel = self.building_params.get("original_fuel_type", None)
        retrofit_fuel = self.building_params.get("retrofit_fuel_type", None)

        fuel_mappings = {
            "natural_gas": "GAS",
            "fuel_oil": "OIL",
            "electricity": "ELEC",
            "propane": "LPG",
            "hybrid_gas": "HPL",
            "hybrid_npa": "NPH",
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

        for fuel in ["electricity", "natural_gas", "propane", "fuel_oil"]:
            annual_fuel_consump = self._annual_energy_by_fuel[fuel]
            emissions_factor = EMISSION_FACTORS.get(fuel, 0)

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

        self.baseline_consumption.resample(resample_string).sum().to_csv(
            "./outputs/{}_baseline_consump.csv".format(self.building_id)
        )

        self.retrofit_consumption.resample(resample_string).sum().to_csv(
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

    def _sum_end_use_figures(self, cost_figure) -> pd.DataFrame:
        """
        cost_figure must be in [
            "install_cost", "depreciation", "stranded_value",
            "elec_consump_annual", "gas_consump_annual", "elec_peak_annual", "gas_peak_annual"
        ]
        """
        costs = {}

        stoves = self.end_uses.get("stove")

        for stove_id, stove in stoves.items():
            costs[stove_id + "_{}".format(cost_figure)] = getattr(stove, cost_figure)

        costs_df = pd.DataFrame(costs)
        costs_df.index = self.years_vec

        costs_df["total_{}".format(cost_figure)] = costs_df.sum(axis=1)

        return costs_df

    #TODO: Remove legacy ResStock code from Holyoke deliverable
    @staticmethod
    def _resstock_timeseries_connector(state: str, scenario: int, building_id: int) -> pd.DataFrame:
        """
        ResStock connection for the 2022 release 1.1 for timeseries data

        Args:
            state (str): The state code
            scenario (int): The simulation scenario
            building_id (int): The ID of the individual building
        """
        BUILDING_BASE_URL = "https://oedi-data-lake.s3.amazonaws.com/"\
                    "nrel-pds-building-stock/end-use-load-profiles-for-us-building-stock/2022/"\
                    "resstock_amy2018_release_1.1/timeseries_individual_buildings/by_state/"

        building_url = BUILDING_BASE_URL + "upgrade={0}/state={1}/{2}-{0}.parquet".format(
            scenario, state, building_id
        )

        response = pd.read_parquet(building_url).set_index("timestamp")
        # Shift timestamps from time-ending to time-beginning
        response.index = response.index.shift(-1, "15T")

        return response

    #TODO: Read in metadata so we can get the ResStock input data for scenarios
