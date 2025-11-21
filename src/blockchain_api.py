"""Module for interacting with Moralis API for blockchain data."""
import os
import json
import requests
import time
from typing import Dict, List, Optional, Set
from dotenv import load_dotenv

load_dotenv()


class BlockchainExplorerAPI:
    """Client for Moralis Web3 API with local caching."""

    def __init__(self, blockchain: str = "ethereum", api_key: Optional[str] = None, incident_id: Optional[str] = None):
        """
        Initialize the Moralis API client.

        Args:
            blockchain: The blockchain to query ("ethereum" or "bsc")
            api_key: Moralis API key (defaults to MORALIS_API_KEY env var)
            incident_id: Incident ID for cache directory organization
        """
        self.blockchain = blockchain
        self.api_key = api_key or os.getenv('MORALIS_API_KEY')
        self.base_url = "https://deep-index.moralis.io/api/v2.2"
        self.incident_id = incident_id

        # Setup cache directory
        if self.incident_id:
            self.cache_dir = os.path.join("moralis-cache", self.incident_id)
            os.makedirs(self.cache_dir, exist_ok=True)
        else:
            self.cache_dir = None

        # Map blockchain names to Moralis chain identifiers
        self.chain_map = {
            "ethereum": "0x1",  # Ethereum Mainnet
            "bsc": "0x38",      # BSC Mainnet
            "eth": "0x1"
        }

        self.headers = {
            "X-API-Key": self.api_key if self.api_key else "",
            "accept": "application/json"
        }

    def _get_cache_path(self, address: str, transaction_type: str) -> Optional[str]:
        """
        Get the cache file path for an address and transaction type.

        Args:
            address: Blockchain address
            transaction_type: Type of transaction (normal, token)

        Returns:
            Path to cache file, or None if caching is disabled
        """
        if not self.cache_dir:
            return None

        safe_address = address.lower().replace('0x', '')
        filename = f"{safe_address}_{transaction_type}.json"
        return os.path.join(self.cache_dir, filename)

    def _read_cache(self, address: str, transaction_type: str) -> Optional[List[Dict]]:
        """
        Read cached response for an address.

        Args:
            address: Blockchain address
            transaction_type: Type of transaction (normal, token)

        Returns:
            Cached transaction list, or None if not cached
        """
        cache_path = self._get_cache_path(address, transaction_type)
        if not cache_path or not os.path.exists(cache_path):
            return None

        try:
            with open(cache_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Error reading cache for {address}: {e}")
            return None

    def _write_cache(self, address: str, transaction_type: str, data: List[Dict]) -> None:
        """
        Write response to cache.

        Args:
            address: Blockchain address
            transaction_type: Type of transaction (normal, token)
            data: Transaction data to cache
        """
        cache_path = self._get_cache_path(address, transaction_type)
        if not cache_path:
            return

        try:
            with open(cache_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Error writing cache for {address}: {e}")

    def get_normal_transactions(self, address: str, startblock: int = 0, endblock: int = 99999999) -> List[Dict]:
        """
        Get normal transactions for an address using Moralis API with caching.

        Args:
            address: The blockchain address
            startblock: Starting block number (not used by Moralis)
            endblock: Ending block number (not used by Moralis)

        Returns:
            List of transaction dictionaries
        """
        # Check cache first
        cached_data = self._read_cache(address, "normal")
        if cached_data is not None:
            print(f"Using cached normal transactions for {address[:10]}...")
            return cached_data

        if not self.api_key:
            print(f"Warning: No Moralis API key. Using mock data.")
            return self._get_mock_transactions(address)

        chain = self.chain_map.get(self.blockchain, "0x1")
        url = f"{self.base_url}/{address}"

        params = {
            "chain": chain,
            "limit": 100  # Moralis returns up to 100 per request
        }

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            # Convert Moralis format to Etherscan-like format for compatibility
            transactions = []
            for tx in data.get("result", []):
                to_addr = tx.get("to_address")
                transactions.append({
                    "blockNumber": str(tx.get("block_number", "")),
                    "timeStamp": str(tx.get("block_timestamp", "")),
                    "hash": tx.get("hash", ""),
                    "from": tx.get("from_address", "").lower(),
                    "to": to_addr.lower() if to_addr else "",
                    "value": str(tx.get("value", "0")),
                    "gas": str(tx.get("gas", "21000")),
                    "gasPrice": str(tx.get("gas_price", "0")),
                    "isError": "1" if tx.get("receipt_status") == "0" else "0",
                    "input": tx.get("input", "0x")
                })

            # Write to cache
            self._write_cache(address, "normal", transactions)

            return transactions

        except requests.exceptions.RequestException as e:
            print(f"Error fetching transactions from Moralis: {e}")
            return self._get_mock_transactions(address)

    def get_token_transfers(self, address: str, startblock: int = 0, endblock: int = 99999999) -> List[Dict]:
        """
        Get ERC20 token transfer transactions for an address using Moralis API with caching.

        Args:
            address: The blockchain address
            startblock: Starting block number (not used by Moralis)
            endblock: Ending block number (not used by Moralis)

        Returns:
            List of token transfer dictionaries
        """
        # Check cache first
        cached_data = self._read_cache(address, "token")
        if cached_data is not None:
            print(f"Using cached token transfers for {address[:10]}...")
            return cached_data

        if not self.api_key:
            print(f"Warning: No Moralis API key. Using mock data.")
            return self._get_mock_token_transfers(address)

        chain = self.chain_map.get(self.blockchain, "0x1")
        url = f"{self.base_url}/{address}/erc20/transfers"

        params = {
            "chain": chain,
            "limit": 100  # Moralis returns up to 100 per request
        }

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            # Convert Moralis format to Etherscan-like format for compatibility
            transfers = []
            for transfer in data.get("result", []):
                to_addr = transfer.get("to_address")
                from_addr = transfer.get("from_address")
                contract_addr = transfer.get("address")
                transfers.append({
                    "blockNumber": str(transfer.get("block_number", "")),
                    "timeStamp": str(transfer.get("block_timestamp", "")),
                    "hash": transfer.get("transaction_hash", ""),
                    "from": from_addr.lower() if from_addr else "",
                    "to": to_addr.lower() if to_addr else "",
                    "value": str(transfer.get("value", "0")),
                    "tokenName": transfer.get("token_name", "UNKNOWN"),
                    "tokenSymbol": transfer.get("token_symbol", "UNK"),
                    "tokenDecimal": str(transfer.get("token_decimals", "18")),
                    "contractAddress": contract_addr.lower() if contract_addr else "",
                    "gas": "65000",
                    "gasPrice": "0"
                })

            # Write to cache
            self._write_cache(address, "token", transfers)

            return transfers

        except requests.exceptions.RequestException as e:
            print(f"Error fetching token transfers from Moralis: {e}")
            return self._get_mock_token_transfers(address)

    def get_all_transactions(self, address: str, limit: int = 100) -> Dict:
        """
        Get both normal transactions and token transfers for an address.

        Args:
            address: The blockchain address
            limit: Maximum number of transactions to return per type

        Returns:
            Dictionary with 'normal' and 'token' transaction lists
        """
        print(f"Fetching transactions for {address} on {self.blockchain} via Moralis...")

        normal_txs = self.get_normal_transactions(address)
        time.sleep(0.2)  # Rate limiting
        token_txs = self.get_token_transfers(address)

        # Limit results
        return {
            "normal": normal_txs[:limit] if normal_txs else [],
            "token": token_txs[:limit] if token_txs else []
        }

    def get_network_transactions(self, primary_address: str, depth: int = 2, limit_per_address: int = 20) -> Dict:
        """
        Recursively fetch transactions for a network up to specified depth.

        Args:
            primary_address: Starting address
            depth: Network depth to explore (1 = only primary, 2 = primary + connected, etc.)
            limit_per_address: Max transactions to fetch per address

        Returns:
            Dictionary with combined 'normal' and 'token' transaction lists
        """
        print(f"\n{'='*80}")
        print(f"Fetching network transactions at depth {depth} for {primary_address}")
        print(f"{'='*80}\n")

        # Track processed addresses to avoid duplicates
        processed_addresses: Set[str] = set()
        all_normal_txs = []
        all_token_txs = []

        # Queue: (address, current_depth)
        queue = [(primary_address.lower(), 0)]

        while queue:
            current_address, current_depth = queue.pop(0)

            # Skip if already processed or depth exceeded
            if current_address in processed_addresses or current_depth >= depth:
                continue

            processed_addresses.add(current_address)
            print(f"Depth {current_depth + 1}/{depth}: Fetching {current_address[:10]}... ({len(processed_addresses)} addresses processed)")

            # Fetch transactions for current address
            txs = self.get_all_transactions(current_address, limit=limit_per_address)

            # Add to combined results
            all_normal_txs.extend(txs.get("normal", []))
            all_token_txs.extend(txs.get("token", []))

            # If we haven't reached max depth, add connected addresses to queue
            if current_depth < depth - 1:
                connected_addresses = set()

                # Extract addresses from normal transactions
                for tx in txs.get("normal", []):
                    from_addr = tx.get("from", "").lower()
                    to_addr = tx.get("to", "").lower()
                    if from_addr and from_addr != current_address and from_addr not in processed_addresses:
                        connected_addresses.add(from_addr)
                    if to_addr and to_addr != current_address and to_addr not in processed_addresses:
                        connected_addresses.add(to_addr)

                # Extract addresses from token transfers
                for tx in txs.get("token", []):
                    from_addr = tx.get("from", "").lower()
                    to_addr = tx.get("to", "").lower()
                    if from_addr and from_addr != current_address and from_addr not in processed_addresses:
                        connected_addresses.add(from_addr)
                    if to_addr and to_addr != current_address and to_addr not in processed_addresses:
                        connected_addresses.add(to_addr)

                # Add connected addresses to queue for next depth
                for addr in connected_addresses:
                    queue.append((addr, current_depth + 1))

                print(f"  -> Found {len(connected_addresses)} new addresses at depth {current_depth + 2}")

        print(f"\n{'='*80}")
        print(f"Network fetch complete: {len(processed_addresses)} addresses, {len(all_normal_txs)} normal txs, {len(all_token_txs)} token txs")
        print(f"{'='*80}\n")

        return {
            "normal": all_normal_txs,
            "token": all_token_txs
        }

    def _get_mock_transactions(self, address: str) -> List[Dict]:
        """Generate mock normal transaction data."""
        import random

        mock_txs = []
        for i in range(10):
            is_incoming = random.random() > 0.5
            other_address = f"0x{''.join([format(random.randint(0, 15), 'x') for _ in range(40)])}"

            mock_txs.append({
                "blockNumber": str(20000000 + i * 1000),
                "timeStamp": str(1700000000 + i * 86400),
                "hash": f"0x{''.join([format(random.randint(0, 15), 'x') for _ in range(64)])}",
                "from": other_address if is_incoming else address.lower(),
                "to": address.lower() if is_incoming else other_address,
                "value": str(random.randint(1000000000000000, 10000000000000000000)),
                "gas": "21000",
                "gasPrice": str(random.randint(1000000000, 50000000000)),
                "isError": "0",
                "input": "0x"
            })

        return mock_txs

    def _get_mock_token_transfers(self, address: str) -> List[Dict]:
        """Generate mock token transfer data."""
        import random

        token_names = ["USDT", "USDC", "DAI", "WETH", "BUSD"]
        mock_transfers = []

        for i in range(5):
            is_incoming = random.random() > 0.5
            other_address = f"0x{''.join([format(random.randint(0, 15), 'x') for _ in range(40)])}"
            contract_address = f"0x{''.join([format(random.randint(0, 15), 'x') for _ in range(40)])}"
            token_name = random.choice(token_names)

            mock_transfers.append({
                "blockNumber": str(20000000 + i * 1000),
                "timeStamp": str(1700000000 + i * 86400),
                "hash": f"0x{''.join([format(random.randint(0, 15), 'x') for _ in range(64)])}",
                "from": other_address if is_incoming else address.lower(),
                "to": address.lower() if is_incoming else other_address,
                "value": str(random.randint(1000000000000000000, 1000000000000000000000)),
                "tokenName": token_name,
                "tokenSymbol": token_name,
                "tokenDecimal": "18",
                "contractAddress": contract_address,
                "gas": "65000",
                "gasPrice": str(random.randint(1000000000, 50000000000))
            })

        return mock_transfers


if __name__ == "__main__":
    # Test the Moralis API
    moralis_api = BlockchainExplorerAPI(blockchain="ethereum")
    address = "0x9c55f83Ae6D0093574F85da951419258D476Ae46"

    print(f"Testing Moralis API for {address}")
    print("=" * 80)

    txs = moralis_api.get_all_transactions(address, limit=5)
    print(f"\nNormal transactions: {len(txs['normal'])}")
    print(f"Token transfers: {len(txs['token'])}")

    if txs['normal']:
        print(f"\nSample normal tx: {txs['normal'][0]['hash']}")
        print(f"  From: {txs['normal'][0]['from']}")
        print(f"  To: {txs['normal'][0]['to']}")

    if txs['token']:
        print(f"\nSample token transfer: {txs['token'][0]['hash']}")
        print(f"  Token: {txs['token'][0].get('tokenName', 'N/A')}")
        print(f"  From: {txs['token'][0]['from']}")
        print(f"  To: {txs['token'][0]['to']}")
