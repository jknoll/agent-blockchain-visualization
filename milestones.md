# Development Milestones

## Milestone 1

Create an agent using the Claude Agents Python SDK which:
1) Retrieves, for example wallet address, contract address, or transaction ID from a datastore. For the first version, this can be read from a local file. For the final version, it should be dynamically retrieved from an online source to be determined. It should be an address or transaction which is involved in some malicious incident in its on-chain activity.

Incident ingestion: For each incident you identify (from a feed), you have a list of victim/attacker addresses and/or contract address(es).
	2.	Address data pull: Use Etherscan (or BscScan) API to get all relevant transactions for each address (both normal txn history and token transfers).
	•	Eg: call txlist for the victim address to get hash, from, to, blockNumber, etc.  ￼
	•	For token transfers: call tokentx endpoint to get contract address info.  ￼
	3.	Build graph edges/nodes: From transaction data, derive edges (e.g., from → to, with tx hash as edge ID, contract address as node if needed) and nodes (addresses + contracts) with attributes (e.g., token amount, time, chain).
	4.	TRM enrichment: Pass each node (address or contract) into TRM’s wallet/entity screening API to get risk-score and metadata. For instance, TRM’s “Wallet Screening” product provides “a wallet’s trading volume, a full list of risks and attribution” for an address. Use their public, free Sanctions API.  https://docs.sanctions.trmlabs.com/#operation/PublicV1SanctionsScreeningPost
  relying on etherscan or bnbscan to retrieve the wallet interactions necessary to build the graph. Implement these changes and regenerate the
  visualization. 
	5.	Visualization: Build a JSON graph structure ready for three.js (e.g., nodes with risk_score, incident_id, chain; edges with tx_hash, amount, timestamp). Then render it in three.js. Create a three.js force directed graph visualization of the incident, where the node color is the entity's risk score, and edges exist where there is activity between entities (transaction flows with direction, where the visualized size of the edge is based on the interaction volume). 

4) Generate an .html output file in /output/[incident-id] which includes the embedded and explorable three.js visualization as well as a technical summary of the incident.

Stop after implementing Milestone 1 and wait for user input and validation before proceeding to Milestone 2.

## Milestone 2
1) Take the output /output/[incident-id] and publish it via the sanity.io https://www.sanity.io/ headless content management system.

## Milestone 3
1) 