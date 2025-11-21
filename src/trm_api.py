"""Module for interacting with TRM Labs BlockInt API."""
import os
import requests
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()


class TRMLabsAPI:
    """Client for TRM Labs BlockInt API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the TRM Labs API client.

        Args:
            api_key: TRM Labs API key (defaults to TRM_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('TRM_API_KEY')
        self.sanctions_url = "https://api.trmlabs.com/public/v1/sanctions/screening"
        self.headers = {
            "Authorization": f"Basic {self.api_key}" if self.api_key else "",
            "Content-Type": "application/json"
        }

    def screen_address(self, address: str, chain: str = "ethereum") -> Dict:
        """
        Screen an address using TRM Sanctions API.

        Args:
            address: The blockchain address
            chain: The blockchain network

        Returns:
            Dictionary containing screening results with risk data
        """
        if not self.api_key:
            print(f"Warning: No TRM API key. Using mock sanctions data for {address[:10]}...")
            return self._get_mock_sanctions_data(address)

        # Map chain names to TRM format
        chain_map = {
            "ethereum": "ethereum",
            "bsc": "bsc",
            "binance-smart-chain": "bsc"
        }
        trm_chain = chain_map.get(chain.lower(), chain.lower())

        payload = [{
            "address": address,
            "chain": trm_chain
        }]

        try:
            response = requests.post(
                self.sanctions_url,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            results = response.json()

            if results and len(results) > 0:
                return results[0]
            else:
                return self._get_mock_sanctions_data(address)

        except requests.exceptions.RequestException as e:
            print(f"Error screening address: {e}")
            return self._get_mock_sanctions_data(address)

    def get_address_info(self, address: str, blockchain: str = "ethereum") -> Dict:
        """
        Get information about a blockchain address using sanctions screening.

        Args:
            address: The blockchain address
            blockchain: The blockchain network (default: ethereum)

        Returns:
            Dictionary containing address information
        """
        screening_result = self.screen_address(address, blockchain)

        # Transform sanctions data to address info format
        return {
            "address": address,
            "blockchain": blockchain,
            "entity": {
                "name": screening_result.get("name", "Unknown Entity"),
                "category": screening_result.get("category", "unknown")
            },
            "labels": screening_result.get("labels", []),
            "is_sanctioned": screening_result.get("isSanctioned", False)
        }

    def get_address_risk(self, address: str, blockchain: str = "ethereum") -> Dict:
        """
        Get risk assessment for a blockchain address using sanctions screening.

        Args:
            address: The blockchain address
            blockchain: The blockchain network

        Returns:
            Dictionary containing sanctions status (no risk score without API)
        """
        screening_result = self.screen_address(address, blockchain)
        is_sanctioned = screening_result.get("isSanctioned", False)

        return {
            "address": address,
            "is_sanctioned": is_sanctioned,
            "risk_indicators": screening_result.get("riskIndicators", [])
        }

    def _get_mock_sanctions_data(self, address: str) -> Dict:
        """
        Generate mock sanctions screening data.
        Without TRM API, we cannot determine actual sanctions status.
        Always returns non-sanctioned for mock data.
        """
        return {
            "address": address,
            "chain": "unknown",
            "isSanctioned": False,  # Cannot determine without API
            "name": "Unknown Entity",
            "category": "unknown",
            "labels": [],
            "riskIndicators": []
        }



if __name__ == "__main__":
    # Test the TRM API client
    client = TRMLabsAPI()
    address = "0x0000000000000000000000000000000000000000"

    print("Fetching address info...")
    info = client.get_address_info(address)
    print(f"Entity: {info.get('entity', {}).get('name', 'Unknown')}")

    print("\nFetching risk data...")
    risk = client.get_address_risk(address)
    print(f"Risk Score: {risk.get('risk_score', 'N/A')}")

    print("\nFetching network data...")
    network = client.get_address_network(address)
    print(f"Network nodes: {network.get('metadata', {}).get('total_nodes', 0)}")
