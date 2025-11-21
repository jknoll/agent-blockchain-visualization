# Blockchain Incident Visualization Agent

An intelligent agent built with the Claude Agent SDK that analyzes blockchain security incidents and generates interactive 3D visualizations of transaction networks.

## Overview

This agent automatically:
1. Retrieves blockchain addresses involved in security incidents
2. Fetches structured metadata using TRM Labs BlockInt API
3. Analyzes transaction networks and risk assessments
4. Generates interactive three.js force-directed graph visualizations
5. Creates comprehensive HTML reports with technical summaries

## Features

- **Autonomous Analysis**: Claude-powered agent orchestrates the entire workflow
- **Risk Visualization**: Node colors represent risk scores (red=high, orange=medium, green=low)
- **Network Mapping**: Force-directed graph shows relationships between entities
- **Interactive 3D**: Rotate, zoom, and click nodes for detailed information
- **Transaction Flow**: Edge thickness indicates transaction volume

## Installation

1. Clone the repository:
```bash
git clone https://github.com/jknoll/agent-blockchain-visualization.git
cd agent-blockchain-visualization
```

2. Create a virtual environment and install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your API keys:
# ANTHROPIC_API_KEY=your_anthropic_key
# TRM_API_KEY=your_trm_key (optional - uses mock data if not provided)
```

## Usage

Run the agent:
```bash
python run.py
```

The agent will:
- Load incident data from `data/addresses.json`
- Query the TRM Labs API (or use mock data)
- Generate visualization at `output/[incident-id]/incident.html`
- Provide a detailed analysis summary

## Project Structure

```
agent-blockchain-visualization/
├── src/
│   ├── agent.py              # Main agent orchestration
│   ├── data_retrieval.py     # Data loading from local/remote sources
│   ├── trm_api.py           # TRM Labs API integration
│   └── visualization.py      # Three.js HTML generation
├── data/
│   └── addresses.json        # Incident data store
├── output/                   # Generated visualizations
├── requirements.txt
├── run.py                    # Entry point
└── README.md
```

## Configuration

### Adding Incidents

Edit `data/addresses.json` to add new incidents:

```json
{
  "incidents": [
    {
      "id": "incident-001",
      "name": "Security Incident Name",
      "blockchain": "ethereum",
      "addresses": ["0x..."],
      "transaction_ids": [],
      "description": "Incident description"
    }
  ]
}
```

### API Keys

- **ANTHROPIC_API_KEY** (required): Get from https://console.anthropic.com/
- **TRM_API_KEY** (optional): Get from https://www.trmlabs.com/
  - Without TRM API key, the system uses realistic mock data for testing

## How It Works

The agent uses Claude's tool-calling capabilities to:

1. **get_incident_data**: Load incident from datastore
2. **fetch_address_info**: Query TRM Labs for address details
3. **fetch_risk_assessment**: Get risk scores and indicators
4. **fetch_transaction_network**: Build network graph
5. **generate_visualization**: Create interactive HTML

The agent autonomously decides which tools to use and in what order, adapting to the data it receives.

## Visualization Controls

- **Left click + drag**: Rotate the view
- **Right click + drag**: Pan
- **Scroll**: Zoom in/out
- **Click nodes**: Display detailed information
- **Reset View button**: Return to default camera position
- **Pause/Play button**: Toggle force simulation

## Development

### Running Tests

```bash
# Test data retrieval
python src/data_retrieval.py

# Test TRM API
python src/trm_api.py

# Test visualization
python src/visualization.py
```

### Adding New Tools

Add tool definitions in `src/agent.py` and implement handlers in `process_tool_call()`.

## Requirements

- Python 3.9+
- Anthropic API key
- TRM Labs API key (optional)

## License

ISC

## Contributing

See [milestones.md](milestones.md) for development roadmap.
