"""Module for retrieving blockchain addresses and incident data."""
import json
import os
from typing import Dict, List, Optional


class DataRetrieval:
    """Handles retrieval of blockchain addresses from local or remote sources."""

    def __init__(self, data_file: str = "data/addresses.json"):
        """
        Initialize the data retrieval module.

        Args:
            data_file: Path to the local data file
        """
        self.data_file = data_file

    def load_local_data(self) -> Dict:
        """
        Load blockchain addresses from local JSON file.

        Returns:
            Dictionary containing incident data
        """
        if not os.path.exists(self.data_file):
            raise FileNotFoundError(f"Data file not found: {self.data_file}")

        with open(self.data_file, 'r') as f:
            return json.load(f)

    def get_incident(self, incident_id: Optional[str] = None) -> Dict:
        """
        Get a specific incident or the first one if no ID is provided.

        Args:
            incident_id: Optional incident ID to retrieve

        Returns:
            Dictionary containing incident information
        """
        data = self.load_local_data()
        incidents = data.get('incidents', [])

        if not incidents:
            raise ValueError("No incidents found in data file")

        if incident_id:
            for incident in incidents:
                if incident.get('id') == incident_id:
                    return incident
            raise ValueError(f"Incident with ID '{incident_id}' not found")

        return incidents[0]

    def get_all_incidents(self) -> List[Dict]:
        """
        Get all incidents from the data file.

        Returns:
            List of incident dictionaries
        """
        data = self.load_local_data()
        return data.get('incidents', [])


if __name__ == "__main__":
    # Test the data retrieval
    retriever = DataRetrieval()
    incident = retriever.get_incident()
    print(f"Retrieved incident: {incident['id']}")
    print(f"Addresses: {incident['addresses']}")
