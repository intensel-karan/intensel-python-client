"""
Intensel API Client
===================
This module provides a client for interacting with the Intensel API.

The Intensel API allows users to create projects, add assets, and retrieve hazard, loss, and score data.

Latest version of this script can be found at:
https://github.com/intensel-karan/intensel-python-client/

Last updated: 2024-09-09
"""


import requests
from typing import List, Dict, Literal, Union, Optional
from enum import Enum


class AnalysisType(Enum):
    RCP = "RCP"
    SSP = "SSP"


class OutputFormat(Enum):
    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"
    HTML = "html"


class IntenselAPIClient:
    """
    A client for interacting with the Intensel API.

    This class provides methods to perform various operations such as creating projects,
    adding assets, and retrieving hazard, loss, and score data.

    Attributes:
        base_url (str): The base URL for the Intensel API.
        api_key (str): The API key for authentication.

    Usage:
        client = IntenselAPIClient("YOUR_API_KEY")
        project_name = "My Awesome Project"
        client.create_project(project_name, ["rainfall_flood", "extreme_heat"])
    """

    def __init__(self, api_key: str):
        self.base_url = "https://api.intensel.net/apiv2"
        self.api_key = api_key
        self.headers = {
            'X-Intensel-Api-Key': self.api_key,
        }
        # Verify API key by making a test request
        try:
            response = requests.get(self.base_url, headers=self.headers)
            response.raise_for_status()
        except requests.RequestException:
            raise ValueError("Invalid API key")

    def _make_request(self, method: str, endpoint: str, payload: Optional[Dict] = None, output_format: OutputFormat = OutputFormat.JSON) -> Union[Dict, str]:
        """
        Make a request to the Intensel API.

        Args:
            method (str): The HTTP method to use (e.g., "GET", "POST").
            endpoint (str): The API endpoint to call.
            payload (Optional[Dict]): The payload to send with the request.
            output_format (OutputFormat): The desired output format.

        Returns:
            Union[Dict, str]: The response from the API, either as a dictionary (JSON) or a string (other formats).

        Raises:
            requests.RequestException: If there's an error with the request.
            ValueError: If the response is not in the expected format.
        """
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.request(
                method, url, json=payload, headers=self.headers)
            response.raise_for_status()

            if output_format == OutputFormat.JSON:
                return response.json()
            else:
                return response.text
        except requests.RequestException as e:
            try:
                error_response = response.json()
                raise requests.RequestException(
                    f"API request failed: {error_response}")
            except ValueError:
                raise requests.RequestException(
                    f"API request failed: {str(e)}")
        except ValueError as e:
            raise ValueError(f"Invalid response format: {str(e)}")

    def create_project(self, project_name: str, variables: List[str]) -> Dict:
        """
        Create a new project.

        Args:
            project_name (str): The name of the project.
            variables (List[str]): The list of variables for the project.

        Returns:
            Dict: The response from the API.

        Raises:
            requests.RequestException: If there's an error with the API request.
        """
        payload = {
            "project_name": project_name,
            "variables": variables,
        }
        return self._make_request("POST", "create_project/", payload)

    def add_single_asset(self, project_name: str, asset_data: Dict) -> Dict:
        """
        Add a single asset to a project.

        Args:
            project_name (str): The name of the project.
            asset_data (Dict): The data of the asset to add.

        Returns:
            Dict: The response from the API.

        Raises:
            requests.RequestException: If there's an error with the API request.
        """
        payload = {
            "project_name": project_name,
            "asset_data": asset_data,
        }
        return self._make_request("POST", "add_single_asset/", payload)

    def add_bulk_assets(self, project_name: str, asset_data_list: List[Dict]) -> Dict:
        """
        Add multiple assets to a project in bulk.

        Args:
            project_name (str): The name of the project.
            asset_data_list (List[Dict]): A list of asset data dictionaries.

        Returns:
            Dict: The response from the API.

        Raises:
            requests.RequestException: If there's an error with the API request.
            ValueError: If more than 500 assets are provided.
        """
        if len(asset_data_list) > 500:
            raise ValueError(
                "Maximum of 500 assets can be added in a single request.")

        payload = {
            "project_name": project_name,
            "asset_data": asset_data_list,
        }
        return self._make_request("POST", "add_bulk_assets/", payload)

    def get_project_data(self,
                         data_type: Literal["hazard", "loss", "scores"],
                         project_name: str,
                         analysis_type: AnalysisType,
                         variables: List[str],
                         scenarios: List[str],
                         years: List[str],
                         output_format: OutputFormat = OutputFormat.JSON) -> Union[Dict, str]:
        """
        Get project data (hazard, loss, or scores).

        Args:
            data_type (str): The type of data to retrieve ("hazard", "loss", or "scores").
            project_name (str): The name of the project.
            analysis_type (AnalysisType): The type of analysis (RCP or SSP).
            variables (List[str]): The list of variables to include.
            scenarios (List[str]): The list of scenarios to include.
            years (List[str]): The list of years to include.
            output_format (OutputFormat): The desired output format (default: JSON).

        Returns:
            Union[Dict, str]: The response from the API, either as a dictionary (JSON)
                              or a string (CSV, Excel, HTML).

        Raises:
            requests.RequestException: If there's an error with the API request.
            ValueError: If an invalid data_type is provided.
        """
        if data_type not in ["hazard", "loss", "scores"]:
            raise ValueError(
                "Invalid data_type. Must be 'hazard', 'loss', or 'scores'.")

        payload = {
            "project_name": project_name,
            "analysis_type": analysis_type.value,
            "variables": variables,
            "scenarios": scenarios,
            "years": years,
        }

        endpoint = f"project_{data_type}_data/"
        if output_format != OutputFormat.JSON:
            endpoint += f"?output={output_format.value}"

        return self._make_request("POST", endpoint, payload, output_format)
