"""Main agent orchestration using Claude Agent SDK."""
import os
import json
from typing import Dict, List, Any
from anthropic import Anthropic
from dotenv import load_dotenv

from data_retrieval import DataRetrieval
from blockchain_api import BlockchainExplorerAPI
from trm_api import TRMLabsAPI
from graph_builder import GraphBuilder
from visualization import IncidentVisualizer

load_dotenv()


class BlockchainIncidentAgent:
    """Agent for analyzing and visualizing blockchain security incidents."""

    def __init__(self):
        """Initialize the agent with necessary components."""
        self.anthropic_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.data_retrieval = DataRetrieval()
        self.trm_api = TRMLabsAPI()
        self.visualizer = IncidentVisualizer()
        self.current_incident_id = None  # Track current incident for caching

        # Define tools for the agent
        self.tools = [
            {
                "name": "get_incident_data",
                "description": "Retrieve incident data including blockchain addresses from the local datastore",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "incident_id": {
                            "type": "string",
                            "description": "Optional incident ID to retrieve. If not provided, returns the first incident."
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "fetch_address_info",
                "description": "Fetch detailed information about a blockchain address using TRM Labs API",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "address": {
                            "type": "string",
                            "description": "The blockchain address to query"
                        },
                        "blockchain": {
                            "type": "string",
                            "description": "The blockchain network (default: ethereum)",
                            "default": "ethereum"
                        }
                    },
                    "required": ["address"]
                }
            },
            {
                "name": "fetch_risk_assessment",
                "description": "Fetch risk assessment for a blockchain address",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "address": {
                            "type": "string",
                            "description": "The blockchain address to assess"
                        },
                        "blockchain": {
                            "type": "string",
                            "description": "The blockchain network (default: ethereum)",
                            "default": "ethereum"
                        }
                    },
                    "required": ["address"]
                }
            },
            {
                "name": "fetch_transactions",
                "description": "Fetch transaction history for an address and its network from Etherscan/BscScan API. Returns a cache key to avoid context bloat.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "address": {
                            "type": "string",
                            "description": "The blockchain address to query"
                        },
                        "blockchain": {
                            "type": "string",
                            "description": "The blockchain network (ethereum or bsc)",
                            "default": "ethereum"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of transactions to fetch per address",
                            "default": 30
                        },
                        "network_depth": {
                            "type": "integer",
                            "description": "Network depth to explore (1=only address, 2=address+connected, etc.)",
                            "default": 2
                        }
                    },
                    "required": ["address", "blockchain"]
                }
            },
            {
                "name": "build_transaction_graph",
                "description": "Build graph structure from cached transaction data with optional TRM sanctions screening. Stores network in cache and returns a reference to avoid context bloat.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "cache_key": {
                            "type": "string",
                            "description": "Cache key returned from fetch_transactions"
                        },
                        "primary_address": {
                            "type": "string",
                            "description": "The primary address being analyzed"
                        },
                        "blockchain": {
                            "type": "string",
                            "description": "The blockchain network"
                        },
                        "addresses_to_screen": {
                            "type": "array",
                            "description": "List of addresses to check against TRM Sanctions API (empty array = no screening)",
                            "default": []
                        }
                    },
                    "required": ["cache_key", "primary_address", "blockchain"]
                }
            },
            {
                "name": "generate_visualization",
                "description": "Generate an HTML file with three.js visualization of the incident. Reads network data from cache. NOTE: This should be called AFTER you have completed your analysis, so you can include your comprehensive analysis text in the HTML.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "incident_data": {
                            "type": "object",
                            "description": "Incident information"
                        },
                        "network_cache_key": {
                            "type": "string",
                            "description": "Network cache key returned from build_transaction_graph"
                        },
                        "risk_data": {
                            "type": "object",
                            "description": "Risk assessment data"
                        },
                        "output_path": {
                            "type": "string",
                            "description": "Path where the HTML file should be saved"
                        },
                        "analysis_text": {
                            "type": "string",
                            "description": "Your comprehensive analysis text in markdown format to be displayed in the HTML"
                        }
                    },
                    "required": ["incident_data", "network_cache_key", "risk_data", "output_path", "analysis_text"]
                }
            }
        ]

    def process_tool_call(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        """
        Process a tool call from the agent.

        Args:
            tool_name: Name of the tool to call
            tool_input: Input parameters for the tool

        Returns:
            Result of the tool execution
        """
        if tool_name == "get_incident_data":
            incident_id = tool_input.get("incident_id")
            result = self.data_retrieval.get_incident(incident_id)
            # Store incident ID for caching
            if result and "id" in result:
                self.current_incident_id = result["id"]
            return result

        elif tool_name == "fetch_address_info":
            address = tool_input["address"]
            blockchain = tool_input.get("blockchain", "ethereum")
            result = self.trm_api.get_address_info(address, blockchain)
            return result

        elif tool_name == "fetch_risk_assessment":
            address = tool_input["address"]
            blockchain = tool_input.get("blockchain", "ethereum")
            result = self.trm_api.get_address_risk(address, blockchain)
            return result

        elif tool_name == "fetch_transactions":
            address = tool_input["address"]
            blockchain = tool_input.get("blockchain", "ethereum")
            limit = tool_input.get("limit", 10)
            network_depth = tool_input.get("network_depth", 2)

            # Create blockchain API client with caching support
            blockchain_api = BlockchainExplorerAPI(
                blockchain=blockchain,
                incident_id=self.current_incident_id
            )

            # Use network fetching if depth > 1, otherwise simple fetch
            if network_depth > 1:
                transactions = blockchain_api.get_network_transactions(
                    address,
                    depth=network_depth,
                    limit_per_address=limit
                )
            else:
                transactions = blockchain_api.get_all_transactions(address, limit=limit)

            # Store transactions in a cache file to avoid context bloat
            import os
            import json
            cache_dir = f"transaction-cache/{self.current_incident_id}"
            os.makedirs(cache_dir, exist_ok=True)

            cache_key = f"{address[:10]}_{blockchain}_d{network_depth}_l{limit}"
            cache_path = os.path.join(cache_dir, f"{cache_key}.json")

            with open(cache_path, 'w') as f:
                json.dump(transactions, f)

            # Return just metadata to avoid bloating context
            return {
                "cache_key": cache_key,
                "cache_path": cache_path,
                "address": address,
                "blockchain": blockchain,
                "normal_tx_count": len(transactions.get("normal", [])),
                "token_tx_count": len(transactions.get("token", [])),
                "total_tx_count": len(transactions.get("normal", [])) + len(transactions.get("token", [])),
                "network_depth": network_depth,
                "limit_per_address": limit,
                "message": f"Fetched {len(transactions.get('normal', []))} normal + {len(transactions.get('token', []))} token transactions. Use cache_key '{cache_key}' to build graph."
            }

        elif tool_name == "build_transaction_graph":
            import os
            import json

            cache_key = tool_input["cache_key"]
            primary_address = tool_input["primary_address"]
            blockchain = tool_input["blockchain"]
            addresses_to_screen = tool_input.get("addresses_to_screen", [])

            # Read transactions from cache
            cache_dir = f"transaction-cache/{self.current_incident_id}"
            cache_path = os.path.join(cache_dir, f"{cache_key}.json")

            if not os.path.exists(cache_path):
                return {"error": f"Cache file not found: {cache_path}"}

            with open(cache_path, 'r') as f:
                transactions = json.load(f)

            # Build graph
            builder = GraphBuilder(primary_address, blockchain)
            builder.add_transactions(transactions)

            # Build network with optional TRM sanctions screening
            network = builder.build_network(
                trm_api=self.trm_api,
                addresses_to_screen=addresses_to_screen
            )

            # Store network data in cache to avoid context bloat
            network_cache_dir = f"network-cache/{self.current_incident_id}"
            os.makedirs(network_cache_dir, exist_ok=True)

            network_cache_key = f"network_{primary_address[:10]}_{blockchain}"
            network_cache_path = os.path.join(network_cache_dir, f"{network_cache_key}.json")

            with open(network_cache_path, 'w') as f:
                json.dump(network, f)

            # Return just metadata to avoid bloating context
            return {
                "network_cache_key": network_cache_key,
                "network_cache_path": network_cache_path,
                "total_nodes": network["metadata"]["total_nodes"],
                "total_edges": network["metadata"]["total_edges"],
                "total_transactions": network["metadata"]["total_transactions"],
                "primary_address": network["metadata"]["primary_address"],
                "blockchain": network["metadata"]["blockchain"],
                "message": f"Built network graph with {network['metadata']['total_nodes']} nodes and {network['metadata']['total_edges']} edges. Use network_cache_key '{network_cache_key}' for visualization."
            }

        elif tool_name == "generate_visualization":
            import os
            import json

            incident_data = tool_input["incident_data"]
            network_cache_key = tool_input["network_cache_key"]
            risk_data = tool_input["risk_data"]
            output_path = tool_input["output_path"]
            analysis_text = tool_input.get("analysis_text", "")

            # Read network data from cache
            network_cache_dir = f"network-cache/{self.current_incident_id}"
            network_cache_path = os.path.join(network_cache_dir, f"{network_cache_key}.json")

            if not os.path.exists(network_cache_path):
                return {"error": f"Network cache file not found: {network_cache_path}"}

            with open(network_cache_path, 'r') as f:
                network_data = json.load(f)

            result = self.visualizer.generate_html(
                incident_data, network_data, risk_data, output_path, analysis_text
            )
            return {"status": "success", "path": result}

        else:
            return {"error": f"Unknown tool: {tool_name}"}

    def run(self, user_message: str = None) -> Dict:
        """
        Run the agent to analyze a blockchain incident.

        Args:
            user_message: Optional custom user message

        Returns:
            Dictionary with the result of the analysis
        """
        if user_message is None:
            user_message = """Analyze the blockchain security incident using Etherscan/BscScan data:

1. Retrieve incident data from the local datastore
2. Extract the primary address and blockchain (addresses may be strings or objects with 'address' and 'blockchain' fields)
3. Extract the 'screen_for_sanctions' list from the incident data (default to empty array if not present)
4. Extract the 'network_depth' from the incident data (default to 2 if not present)
5. Fetch transaction history using Etherscan/BscScan API with the specified network_depth:
   - network_depth=1: Only fetch transactions for the primary address
   - network_depth=2: Fetch transactions for primary address + all directly connected addresses
   - network_depth=3+: Recursively expand the network to the specified depth
   - NOTE: fetch_transactions now returns a cache_key instead of full transaction data to avoid context bloat
6. Build a transaction graph using the cache_key:
   - Pass the cache_key from step 5 to build_transaction_graph
   - The tool will read transaction data from cache and build the graph
   - Creates nodes for all addresses involved in transactions
   - Creates edges representing transaction flows
   - ONLY checks TRM Sanctions API for addresses in the 'screen_for_sanctions' list
   - All other addresses default to non-sanctioned (is_sanctioned: False)
   - Returns network_cache_key instead of full network data to avoid context bloat
7. Fetch risk assessment for the primary address
8. Analyze the network metadata (node count, edge count, etc.) and write a comprehensive analysis in markdown format including:
   - Transaction patterns and volumes across the network
   - Network depth and connectivity statistics
   - Risk assessment details
   - Any sanctioned entity connections (if screening was performed)
   - Key findings and recommendations
9. Generate an HTML visualization using the network_cache_key:
   - Pass the network_cache_key from step 6 to generate_visualization
   - Include your comprehensive analysis text in the analysis_text parameter
   - The tool will read the full network data from cache
10. Save output to output/[incident-id]/incident.html

IMPORTANT:
- By default, NO addresses are checked against TRM Sanctions API unless explicitly listed in 'screen_for_sanctions'.
- Network depth allows exploring multi-hop transaction relationships for comprehensive analysis.
- Both transaction and network data are cached to avoid context window bloat - use cache keys to reference the data.
- When calling generate_visualization, use the network_cache_key (not the full network data) and include your full analysis text.

Your comprehensive analysis should include:
- Transaction patterns and volumes across the network
- Network depth and connectivity statistics
- Risk assessment details
- Any sanctioned entity connections (if screening was performed)
- Key findings and recommendations"""

        messages = [{"role": "user", "content": user_message}]

        print("Agent starting analysis...")
        print("-" * 80)

        # Agent loop
        while True:
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=16384,
                tools=self.tools,
                messages=messages
            )

            print(f"\nStop reason: {response.stop_reason}")

            # Check if we're done
            if response.stop_reason == "end_turn":
                # Extract final text response
                final_response = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        final_response += block.text

                print("\nAgent completed analysis!")
                print("-" * 80)
                return {
                    "status": "success",
                    "response": final_response,
                    "messages": messages
                }

            # Process tool calls
            if response.stop_reason == "tool_use":
                # Add assistant response to messages
                messages.append({"role": "assistant", "content": response.content})

                # Process each tool call
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        tool_name = block.name
                        tool_input = block.input

                        print(f"\nTool called: {tool_name}")
                        print(f"Input: {json.dumps(tool_input, indent=2)}")

                        # Execute the tool
                        result = self.process_tool_call(tool_name, tool_input)

                        print(f"Result: {json.dumps(result, indent=2)[:500]}...")

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result)
                        })

                # Add tool results to messages
                messages.append({"role": "user", "content": tool_results})

            else:
                print(f"\nUnexpected stop reason: {response.stop_reason}")
                break

        return {"status": "error", "message": "Agent loop exited unexpectedly"}


def main():
    """Main entry point for the agent."""
    print("=" * 80)
    print("Blockchain Incident Visualization Agent")
    print("=" * 80)
    print()

    # Check for API keys
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("ERROR: ANTHROPIC_API_KEY not found in environment variables")
        print("Please create a .env file with your API key")
        return

    # Initialize and run the agent
    agent = BlockchainIncidentAgent()
    result = agent.run()

    # Print final result
    if result["status"] == "success":
        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)
        print("\n" + result["response"])
    else:
        print(f"\nERROR: {result.get('message', 'Unknown error')}")


if __name__ == "__main__":
    main()
