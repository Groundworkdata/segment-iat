"""
Object for storing incentive information
"""
import os
import requests

from dotenv import load_dotenv


INCENTIVE_API_URI = "https://api.rewiringamerica.org/api/v1/calculator"
DEFAULT_HOUSEHOLD_SIZE = 4
DEFAULT_AMI = 80000 #Approx based on 2022 national median income: https://www.census.gov/library/publications/2023/demo/p60-279.html
DEFAULT_START_DATE = "2020"
DEFAULT_END_DATE = "2100"


class Incentives:
    """
    Object for pulling and storing incentive information. Uses the Rewiring Incentive API:
    https://api.rewiringamerica.org/

    Args:
        zip_code (int): The street segment's zip code, for looking up incentives

    Keyword Args:
        income (int): The assumed household income for a household of 4. Defaults to $80,000

    Attributes:
        incentives (list)

    Methods:
        gather_incentives (list)
    """
    def __init__(self, zip_code: int, income: int = DEFAULT_AMI):
        self.zip_code: int = zip_code

        self._income: int = income

        self._response: list = []
        self._incentives: list = []

    @property
    def incentives(self) -> list:
        if not self._incentives:
            print("Incentives not yet queried. Querying incentives...")
            self.gather_incentives()

        return self._incentives

    def gather_incentives(self) -> list:
        """
        Gather incentives from the RA API
        """
        self._response = self._call_rewiring_api()
        self._incentives = self._format_ra_incentives()
    
    def _call_rewiring_api(self) -> list:
        """
        Call RA incentive API
        """
        load_dotenv()
        MY_KEY = os.environ.get("REWIRING_INCENTIVE_API_KEY")
        headers = {"Authorization": f"Bearer {MY_KEY}"}

        params = {
            "household_income": self._income,
            "household_size": DEFAULT_HOUSEHOLD_SIZE,
            "language": "en",
            "tax_filing": "single",
            "owner_status": "homeowner",
            "zip": self.zip_code,
        }

        response = requests.get(INCENTIVE_API_URI, headers=headers, params=params)
        return response.json()

    def _format_ra_incentives(self) -> list:
        """
        Format the response from the RA incentive API to fit our datamodel for incentives
        
        Datamodel:
            'authority_type': 'federal',
            'program': 'Federal Residential Clean Energy Credit (25D)',
            'items': ['battery_storage_installation'],
            'amount': {'type': 'percent', 'number': 0.3, 'representative': 4800},
            'start_date': '2023',
            'end_date': '2032',

        Desired:
            authority_type (str): federal, state, or local
            program (str): Program name
            items (list): Items eligible for the incentive
            measure (str): Measure eligible for the incentive, maps to segment tool measures
            amount (dict): Dict of incentive amount information
            start_date (int): Start year
            end_date (int): End year (exclusive. this is the stop time)
        """
        formatted_incentives = []

        for i in self._response["incentives"]:
            formatted_incentive = {
                "authority_type": i["authority_type"],
                "program": i["program"],
                "items": i["items"],
                "amount": i["amount"],
                #FIXME: See RA API documentation - we only care about year, but not all returned
                # values are ISO-format, which requires us to assume the response always starts with
                # the year
                "start_date": int(i.get("start_date", DEFAULT_START_DATE)[:4]),
                "end_date": int(i.get("end_date", DEFAULT_END_DATE)[:4])
            }

            formatted_incentives.append(formatted_incentive)

        return formatted_incentives
