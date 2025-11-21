"""Module for building graph structures from blockchain transaction data."""
from typing import Dict, List, Set
from collections import defaultdict


class GraphBuilder:
    """Builds graph nodes and edges from blockchain transactions."""

    def __init__(self, primary_address: str, blockchain: str):
        """
        Initialize the graph builder.

        Args:
            primary_address: The primary address being analyzed
            blockchain: The blockchain network
        """
        self.primary_address = primary_address.lower()
        self.blockchain = blockchain
        self.nodes = {}
        self.edges = []
        self.address_volumes = defaultdict(float)
        self.address_tx_counts = defaultdict(int)

    def add_transactions(self, transactions: Dict[str, List[Dict]]):
        """
        Process transactions and build graph structure.

        Args:
            transactions: Dictionary with 'normal' and 'token' transaction lists
        """
        # Process normal transactions
        for tx in transactions.get('normal', []):
            self._process_transaction(tx, is_token=False)

        # Process token transfers
        for tx in transactions.get('token', []):
            self._process_transaction(tx, is_token=True)

    def _process_transaction(self, tx: Dict, is_token: bool = False):
        """
        Process a single transaction and update graph.

        Args:
            tx: Transaction dictionary
            is_token: Whether this is a token transfer
        """
        from_addr = tx.get('from', '').lower()
        to_addr = tx.get('to', '').lower()
        tx_hash = tx.get('hash', '')
        value = float(tx.get('value', 0))

        # Skip if missing critical data
        if not from_addr or not to_addr or not tx_hash:
            return

        # Skip self-transfers
        if from_addr == to_addr:
            return

        # Convert value based on decimals
        if is_token:
            decimals = int(tx.get('tokenDecimal', 18))
            value = value / (10 ** decimals)
            token_symbol = tx.get('tokenSymbol', 'TOKEN')
        else:
            value = value / (10 ** 18)  # Convert wei to native token
            token_symbol = 'BNB' if self.blockchain == 'bsc' else 'ETH'

        # Track volumes
        self.address_volumes[from_addr] += value
        self.address_volumes[to_addr] += value
        self.address_tx_counts[from_addr] += 1
        self.address_tx_counts[to_addr] += 1

        # Add nodes
        if from_addr not in self.nodes:
            self.nodes[from_addr] = {
                "address": from_addr,
                "type": "source" if from_addr == self.primary_address else "connected"
            }

        if to_addr not in self.nodes:
            self.nodes[to_addr] = {
                "address": to_addr,
                "type": "source" if to_addr == self.primary_address else "connected"
            }

        # Create edge
        edge = {
            "source": from_addr,
            "target": to_addr,
            "tx_hash": tx_hash,
            "volume": value,
            "token": token_symbol,
            "timestamp": tx.get('timeStamp', ''),
            "blockNumber": tx.get('blockNumber', ''),
            "is_token": is_token
        }

        if is_token:
            edge["contractAddress"] = tx.get('contractAddress', '')

        self.edges.append(edge)

    def aggregate_edges(self) -> List[Dict]:
        """
        Aggregate multiple transactions between same addresses into single edges.

        Returns:
            List of aggregated edge dictionaries
        """
        # Group edges by source-target pair
        edge_groups = defaultdict(list)

        for edge in self.edges:
            key = (edge['source'], edge['target'])
            edge_groups[key].append(edge)

        # Aggregate each group
        aggregated_edges = []
        for (source, target), group in edge_groups.items():
            total_volume = sum(e['volume'] for e in group)
            tx_count = len(group)

            # Determine primary token (most common)
            tokens = [e['token'] for e in group]
            primary_token = max(set(tokens), key=tokens.count)

            aggregated_edges.append({
                "source": source,
                "target": target,
                "volume": total_volume,
                "transaction_count": tx_count,
                "token": primary_token,
                "direction": "outbound" if source == self.primary_address else "inbound"
            })

        return aggregated_edges

    def build_network(self, trm_api=None, addresses_to_screen: List[str] = None) -> Dict:
        """
        Build the complete network structure with optional sanctions screening.

        Args:
            trm_api: Optional TRM API client for sanctions screening
            addresses_to_screen: List of addresses to check against TRM Sanctions API (default: empty)

        Returns:
            Dictionary with nodes, edges, and metadata
        """
        if addresses_to_screen is None:
            addresses_to_screen = []

        # Normalize addresses to lowercase for comparison
        addresses_to_screen = [addr.lower() for addr in addresses_to_screen]
        # Get aggregated edges
        aggregated_edges = self.aggregate_edges()

        # Build node list with enrichment
        node_list = []
        for address, node_data in self.nodes.items():
            node = {
                "address": address,
                "type": node_data["type"],
                "entity": "Primary Address" if address == self.primary_address else f"Address {address[:8]}...",
                "transaction_count": self.address_tx_counts[address],
                "total_volume": self.address_volumes[address]
            }

            # Add sanctions status only if address is in screening list
            if trm_api and address in addresses_to_screen:
                try:
                    screening = trm_api.screen_address(address, self.blockchain)
                    node["is_sanctioned"] = screening.get("isSanctioned", False)
                    node["entity"] = screening.get("name", node["entity"])
                except Exception as e:
                    print(f"Warning: Could not screen address {address[:10]}...: {e}")
                    node["is_sanctioned"] = False
            else:
                # Default to non-sanctioned if not in screening list
                node["is_sanctioned"] = False

            # Detect if address is likely a contract vs EOA
            # Heuristic: contracts often have more interactions and higher volumes
            # This is imperfect without actual blockchain queries
            is_likely_contract = (
                self.address_tx_counts[address] > 5 or
                self.address_volumes[address] > 100
            )
            node["is_contract"] = is_likely_contract

            node_list.append(node)

        return {
            "nodes": node_list,
            "edges": aggregated_edges,
            "metadata": {
                "primary_address": self.primary_address,
                "blockchain": self.blockchain,
                "total_nodes": len(node_list),
                "total_edges": len(aggregated_edges),
                "total_transactions": len(self.edges)
            }
        }


if __name__ == "__main__":
    # Test the graph builder
    test_address = "0x2e8a8670b734e260cedbc6d5a05532264aae5c38"
    builder = GraphBuilder(test_address, "bsc")

    # Mock transaction data
    mock_txs = {
        "normal": [
            {
                "hash": "0xabc123",
                "from": "0x1111111111111111111111111111111111111111",
                "to": test_address,
                "value": "1000000000000000000",  # 1 BNB
                "timeStamp": "1700000000",
                "blockNumber": "20000000"
            },
            {
                "hash": "0xdef456",
                "from": test_address,
                "to": "0x2222222222222222222222222222222222222222",
                "value": "500000000000000000",  # 0.5 BNB
                "timeStamp": "1700000100",
                "blockNumber": "20000010"
            }
        ],
        "token": []
    }

    builder.add_transactions(mock_txs)
    network = builder.build_network()

    print(f"Nodes: {len(network['nodes'])}")
    print(f"Edges: {len(network['edges'])}")
    print(f"Metadata: {network['metadata']}")
