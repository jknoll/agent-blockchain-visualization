"""Module for generating three.js visualizations of blockchain incidents."""
import json
from typing import Dict, List
import os


class IncidentVisualizer:
    """Creates three.js force-directed graph visualizations of blockchain incidents."""

    def __init__(self):
        """Initialize the visualizer."""
        pass

    def generate_html(
        self,
        incident_data: Dict,
        network_data: Dict,
        risk_data: Dict,
        output_path: str,
        analysis_text: str = ""
    ) -> str:
        """
        Generate an HTML file with embedded three.js visualization.

        Args:
            incident_data: Incident information
            network_data: Network graph data with nodes and edges
            risk_data: Risk assessment data
            output_path: Path where the HTML file will be saved
            analysis_text: Comprehensive analysis text in markdown format

        Returns:
            Path to the generated HTML file
        """
        # Prepare data for visualization
        nodes = network_data.get('nodes', [])
        edges = network_data.get('edges', [])

        # Generate the HTML content
        html_content = self._create_html_template(
            incident_data=incident_data,
            nodes=nodes,
            edges=edges,
            risk_data=risk_data,
            analysis_text=analysis_text
        )

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Write the HTML file
        with open(output_path, 'w') as f:
            f.write(html_content)

        return output_path

    def _create_html_template(
        self,
        incident_data: Dict,
        nodes: List[Dict],
        edges: List[Dict],
        risk_data: Dict,
        analysis_text: str = ""
    ) -> str:
        """
        Create the HTML template with embedded three.js visualization.

        Args:
            incident_data: Incident information
            nodes: List of network nodes
            edges: List of network edges
            risk_data: Risk assessment data
            analysis_text: Comprehensive analysis text in markdown format

        Returns:
            Complete HTML content as a string
        """
        # Handle edge cases where nodes/edges might not be lists
        if not isinstance(nodes, list):
            nodes = []
        if not isinstance(edges, list):
            edges = []

        # Calculate counts explicitly
        node_count = len(nodes)
        edge_count = len(edges)

        # Convert data to JSON for embedding
        nodes_json = json.dumps(nodes)
        edges_json = json.dumps(edges)

        # Escape analysis text for JavaScript template literal
        escaped_analysis = analysis_text.replace('`', '\\`').replace('$', '\\$') if analysis_text else ""

        # Get risk color based on score
        def get_risk_color(risk_score):
            if risk_score > 70:
                return '#ff0000'  # High risk: red
            elif risk_score > 30:
                return '#ffa500'  # Medium risk: orange
            else:
                return '#00ff00'  # Low risk: green

        incident_id = incident_data.get('id', 'unknown')
        incident_name = incident_data.get('name', 'Unknown Incident')
        incident_desc = incident_data.get('description', 'No description available')

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blockchain Incident Visualization - {incident_name}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0a0e27;
            color: #ffffff;
        }}

        .container {{
            max-width: 1800px;
            margin: 0 auto;
            padding: 20px;
        }}

        header {{
            text-align: center;
            padding: 30px 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            margin-bottom: 30px;
        }}

        h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .incident-id {{
            font-size: 1.2em;
            opacity: 0.9;
        }}

        .content {{
            display: grid;
            grid-template-columns: 1fr 400px;
            gap: 20px;
            margin-bottom: 30px;
        }}

        #visualization {{
            background: #1a1f3a;
            border-radius: 10px;
            height: 700px;
            position: relative;
            overflow: hidden;
        }}

        .sidebar {{
            background: #1a1f3a;
            border-radius: 10px;
            padding: 20px;
            overflow-y: auto;
            max-height: 700px;
        }}

        .section {{
            margin-bottom: 25px;
        }}

        .section h2 {{
            font-size: 1.3em;
            margin-bottom: 15px;
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 8px;
        }}

        .stat {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #2a2f4a;
        }}

        .stat:last-child {{
            border-bottom: none;
        }}

        .stat-label {{
            font-weight: 600;
            opacity: 0.8;
        }}

        .stat-value {{
            font-weight: 700;
        }}

        .risk-high {{
            color: #ff4444;
        }}

        .risk-medium {{
            color: #ffa500;
        }}

        .risk-low {{
            color: #44ff44;
        }}

        .legend {{
            background: #0f1229;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
        }}

        .legend-item {{
            display: flex;
            align-items: center;
            margin: 8px 0;
        }}

        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
            margin-right: 10px;
        }}

        .technical-summary {{
            background: #1a1f3a;
            border-radius: 10px;
            padding: 30px;
            margin-top: 20px;
        }}

        .technical-summary h2 {{
            font-size: 1.8em;
            margin-bottom: 20px;
            color: #667eea;
        }}

        .technical-summary p {{
            line-height: 1.8;
            margin-bottom: 15px;
            opacity: 0.9;
        }}

        .controls {{
            position: absolute;
            top: 10px;
            left: 10px;
            z-index: 1000;
            background: rgba(26, 31, 58, 0.9);
            padding: 10px;
            border-radius: 5px;
        }}

        .controls button {{
            background: #667eea;
            color: white;
            border: none;
            padding: 8px 15px;
            margin: 5px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9em;
        }}

        .controls button:hover {{
            background: #764ba2;
        }}

        .node-info {{
            position: absolute;
            bottom: 10px;
            left: 10px;
            background: rgba(26, 31, 58, 0.95);
            padding: 15px;
            border-radius: 8px;
            max-width: 300px;
            display: none;
        }}

        .node-info.active {{
            display: block;
        }}

        /* Markdown content styling */
        #analysis-content h1, #analysis-content h2, #analysis-content h3 {{
            color: #667eea;
            margin-top: 25px;
            margin-bottom: 15px;
        }}

        #analysis-content h1 {{
            font-size: 1.6em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}

        #analysis-content h2 {{
            font-size: 1.4em;
        }}

        #analysis-content h3 {{
            font-size: 1.2em;
        }}

        #analysis-content ul, #analysis-content ol {{
            margin-left: 20px;
            margin-bottom: 15px;
        }}

        #analysis-content li {{
            margin-bottom: 8px;
        }}

        #analysis-content p {{
            margin-bottom: 15px;
        }}

        #analysis-content code {{
            background: #0f1229;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}

        #analysis-content pre {{
            background: #0f1229;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            margin-bottom: 15px;
        }}

        #analysis-content table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}

        #analysis-content th, #analysis-content td {{
            border: 1px solid #2a2f4a;
            padding: 10px;
            text-align: left;
        }}

        #analysis-content th {{
            background: #0f1229;
            font-weight: bold;
        }}

        #analysis-content blockquote {{
            border-left: 4px solid #667eea;
            padding-left: 15px;
            margin-left: 0;
            opacity: 0.8;
        }}

        #analysis-content strong {{
            color: #8899ff;
        }}

        #analysis-content a {{
            color: #667eea;
            text-decoration: none;
        }}

        #analysis-content a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{incident_name}</h1>
            <div class="incident-id">Incident ID: {incident_id}</div>
        </header>

        <div class="content">
            <div id="visualization">
                <div class="controls">
                    <button onclick="resetCamera()">Reset View</button>
                    <button onclick="toggleAnimation()">Pause/Play</button>
                </div>
                <div id="node-info" class="node-info"></div>
            </div>

            <div class="sidebar">
                <div class="section">
                    <h2>Network Statistics</h2>
                    <div class="stat">
                        <span class="stat-label">Total Nodes:</span>
                        <span class="stat-value">{node_count}</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Total Edges:</span>
                        <span class="stat-value">{edge_count}</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Network Depth:</span>
                        <span class="stat-value">1</span>
                    </div>
                </div>

                <div class="section">
                    <h2>Sanctions Status</h2>
                    <div class="stat">
                        <span class="stat-label">Primary Address:</span>
                        <span class="stat-value {'risk-high' if risk_data.get('is_sanctioned') else ''}">{{'SANCTIONED' if risk_data.get('is_sanctioned') else 'Not Sanctioned'}}</span>
                    </div>
                </div>

                <div class="legend">
                    <h3 style="margin-bottom: 10px; font-size: 1.1em;">Node Colors</h3>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #cc0000;"></div>
                        <span>Sanctioned EOA</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #ff6666;"></div>
                        <span>Sanctioned Contract</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #0066cc;"></div>
                        <span>Non-sanctioned EOA</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #66b3ff;"></div>
                        <span>Non-sanctioned Contract</span>
                    </div>
                </div>

                <div class="legend" style="margin-top: 15px;">
                    <h3 style="margin-bottom: 10px; font-size: 1.1em;">Transaction Flow</h3>
                    <p style="font-size: 0.85em; line-height: 1.6; opacity: 0.9; margin-bottom: 10px;">
                        <strong>Edge Thickness:</strong> Represents transaction volume (thicker = higher volume)
                    </p>
                    <p style="font-size: 0.85em; line-height: 1.6; opacity: 0.9;">
                        <strong>Arrow Direction:</strong> Blue cone shows direction of fund flow (source → target)
                    </p>
                </div>

                <div class="section" style="margin-top: 20px;">
                    <h2>Controls</h2>
                    <p style="font-size: 0.9em; line-height: 1.6; opacity: 0.8;">
                        • Left click + drag to rotate<br>
                        • Right click + drag to pan<br>
                        • Scroll to zoom<br>
                        • Click on nodes for details
                    </p>
                </div>
            </div>
        </div>

        <div class="technical-summary">
            <h2>Technical Summary</h2>
            <p><strong>Description:</strong> {incident_desc}</p>
            <p><strong>Blockchain:</strong> {incident_data.get('blockchain', 'Unknown')}</p>
            <p><strong>Analysis:</strong> This visualization represents the transaction network associated with the incident.
            Each node represents a blockchain address or entity, with color indicating risk level. Edge thickness
            represents transaction volume between entities. The graph uses a force-directed layout to show relationships
            and clustering patterns in the network.</p>
            <p><strong>Data Source:</strong> Moralis API + TRM Labs Risk Assessment</p>
        </div>

        <div class="analysis-section" style="background: #1a1f3a; border-radius: 10px; padding: 30px; margin-top: 20px;">
            <h2 style="font-size: 1.8em; margin-bottom: 20px; color: #667eea;">Comprehensive Analysis</h2>
            <div id="analysis-content" style="line-height: 1.8; opacity: 0.95;">
                <!-- Analysis will be rendered here by marked.js -->
            </div>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://unpkg.com/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script>
        // Render markdown analysis
        const analysisText = `{escaped_analysis}`;
        if (analysisText && analysisText.trim()) {{
            document.getElementById('analysis-content').innerHTML = marked.parse(analysisText);
        }} else {{
            document.getElementById('analysis-content').innerHTML = '<p style="opacity: 0.7;"><em>No detailed analysis available. The agent did not provide comprehensive analysis text.</em></p>';
        }}
    </script>
    <script>
        // Parse data
        const nodes = {nodes_json};
        const edges = {edges_json};

        // Three.js setup
        const container = document.getElementById('visualization');
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0a0e27);

        const camera = new THREE.PerspectiveCamera(
            75,
            container.clientWidth / container.clientHeight,
            0.1,
            1000
        );
        camera.position.z = 30;

        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(container.clientWidth, container.clientHeight);
        container.appendChild(renderer.domElement);

        // Orbit controls
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;

        // Lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        scene.add(ambientLight);

        const pointLight = new THREE.PointLight(0xffffff, 0.8);
        pointLight.position.set(10, 10, 10);
        scene.add(pointLight);

        // Create node meshes
        const nodeMeshes = [];
        const nodePositions = new Map();

        // Function to get color based on sanctions status and address type
        function getNodeColor(node) {{
            const is_sanctioned = node.is_sanctioned || false;
            const is_contract = node.is_contract || false;

            if (is_sanctioned) {{
                // Sanctioned: Red (dark for EOA, light for contract)
                return is_contract ? 0xff6666 : 0xcc0000;  // Light red : Dark red
            }} else {{
                // Non-sanctioned: Blue (dark for EOA, light for contract)
                return is_contract ? 0x66b3ff : 0x0066cc;  // Light blue : Dark blue
            }}
        }}

        // Create nodes in a circle initially (smaller radius for better initial layout)
        const radius = Math.min(8, 4 + nodes.length * 0.3);  // Scale with node count
        nodes.forEach((node, index) => {{
            const angle = (index / nodes.length) * Math.PI * 2;
            const x = Math.cos(angle) * radius;
            const y = Math.sin(angle) * radius;
            const z = (Math.random() - 0.5) * 3;

            const nodeColor = getNodeColor(node);
            const geometry = new THREE.SphereGeometry(0.5, 32, 32);
            const material = new THREE.MeshPhongMaterial({{
                color: nodeColor,
                emissive: nodeColor,
                emissiveIntensity: 0.2
            }});

            const sphere = new THREE.Mesh(geometry, material);
            sphere.position.set(x, y, z);
            sphere.userData = node;

            scene.add(sphere);
            nodeMeshes.push(sphere);
            nodePositions.set(node.address, sphere.position);
        }});

        // Create edges with proper sizing and direction arrows
        const edgeMeshes = [];
        const minVolume = Math.min(...edges.map(e => e.volume));
        const maxVolume = Math.max(...edges.map(e => e.volume));

        edges.forEach(edge => {{
            const sourcePos = nodePositions.get(edge.source);
            const targetPos = nodePositions.get(edge.target);

            if (sourcePos && targetPos) {{
                // Calculate edge thickness based on volume (0.05 to 0.3)
                const volumeRatio = (edge.volume - minVolume) / (maxVolume - minVolume || 1);
                const thickness = 0.05 + volumeRatio * 0.25;

                // Create cylinder for the edge
                const direction = new THREE.Vector3().subVectors(targetPos, sourcePos);
                const distance = direction.length();
                const edgeMaterial = new THREE.MeshPhongMaterial({{
                    color: 0x667eea,
                    opacity: 0.7,
                    transparent: true,
                    shininess: 30
                }});

                const cylinderGeometry = new THREE.CylinderGeometry(thickness, thickness, distance, 8);
                const cylinder = new THREE.Mesh(cylinderGeometry, edgeMaterial);

                // Position and orient the cylinder
                cylinder.position.copy(sourcePos).add(direction.multiplyScalar(0.5));
                cylinder.quaternion.setFromUnitVectors(
                    new THREE.Vector3(0, 1, 0),
                    direction.clone().normalize()
                );

                scene.add(cylinder);

                // Create arrow head (cone) at the target to show direction
                const arrowSize = thickness * 3;
                const coneGeometry = new THREE.ConeGeometry(arrowSize, arrowSize * 2, 8);
                const coneMaterial = new THREE.MeshPhongMaterial({{
                    color: 0x8899ff,
                    opacity: 0.9,
                    transparent: true
                }});
                const cone = new THREE.Mesh(coneGeometry, coneMaterial);

                // Position cone at target, pointing in direction of flow
                const arrowDirection = direction.clone().normalize();
                const arrowPos = targetPos.clone().sub(arrowDirection.multiplyScalar(0.5 + arrowSize));
                cone.position.copy(arrowPos);
                cone.quaternion.setFromUnitVectors(
                    new THREE.Vector3(0, 1, 0),
                    arrowDirection
                );

                scene.add(cone);

                edgeMeshes.push({{
                    cylinder,
                    cone,
                    source: sourcePos,
                    target: targetPos,
                    thickness
                }});
            }}
        }});

        // Force-directed simulation
        let animating = true;

        function applyForces() {{
            if (!animating) return;

            const repulsionStrength = 1.5;      // Reduced from 2
            const attractionStrength = 0.08;    // Increased from 0.01 (8x stronger)
            const desiredEdgeLength = 5;        // Target edge length
            const springStrength = 0.02;        // Spring force to maintain edge length
            const damping = 0.9;

            nodeMeshes.forEach((node, i) => {{
                const velocity = node.userData.velocity || new THREE.Vector3(0, 0, 0);

                // Repulsion between nodes (inverse square law)
                nodeMeshes.forEach((other, j) => {{
                    if (i !== j) {{
                        const diff = new THREE.Vector3().subVectors(node.position, other.position);
                        const distance = diff.length();
                        if (distance > 0 && distance < 20) {{  // Only repel nearby nodes
                            const force = repulsionStrength / (distance * distance);
                            diff.normalize().multiplyScalar(force);
                            velocity.add(diff);
                        }}
                    }}
                }});

                // Spring forces along edges (Hooke's law)
                edges.forEach(edge => {{
                    if (edge.source === node.userData.address) {{
                        const targetPos = nodePositions.get(edge.target);
                        if (targetPos) {{
                            const diff = new THREE.Vector3().subVectors(targetPos, node.position);
                            const distance = diff.length();

                            // Spring force: F = k * (distance - desiredLength)
                            const displacement = distance - desiredEdgeLength;
                            const force = springStrength * displacement;

                            diff.normalize().multiplyScalar(force);
                            velocity.add(diff);
                        }}
                    }}
                    // Bidirectional attraction for connected nodes
                    if (edge.target === node.userData.address) {{
                        const sourcePos = nodePositions.get(edge.source);
                        if (sourcePos) {{
                            const diff = new THREE.Vector3().subVectors(sourcePos, node.position);
                            const distance = diff.length();
                            const displacement = distance - desiredEdgeLength;
                            const force = springStrength * displacement;
                            diff.normalize().multiplyScalar(force);
                            velocity.add(diff);
                        }}
                    }}
                }});

                // Apply damping
                velocity.multiplyScalar(damping);

                // Update position
                node.position.add(velocity);
                node.userData.velocity = velocity;
            }});

            // Update edge positions (cylinders and cones)
            edgeMeshes.forEach(edge => {{
                // Update cylinder position and orientation
                const direction = new THREE.Vector3().subVectors(edge.target, edge.source);
                const distance = direction.length();

                // Resize cylinder to new distance
                edge.cylinder.scale.y = distance / edge.cylinder.geometry.parameters.height;

                // Position at midpoint
                edge.cylinder.position.copy(edge.source).add(direction.clone().multiplyScalar(0.5));

                // Orient cylinder
                edge.cylinder.quaternion.setFromUnitVectors(
                    new THREE.Vector3(0, 1, 0),
                    direction.clone().normalize()
                );

                // Update arrow cone position
                const arrowDirection = direction.clone().normalize();
                const arrowSize = edge.thickness * 3;
                const arrowPos = edge.target.clone().sub(arrowDirection.multiplyScalar(0.5 + arrowSize));
                edge.cone.position.copy(arrowPos);
                edge.cone.quaternion.setFromUnitVectors(
                    new THREE.Vector3(0, 1, 0),
                    arrowDirection
                );
            }});
        }}

        // Mouse interaction
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();
        const nodeInfo = document.getElementById('node-info');

        container.addEventListener('click', (event) => {{
            const rect = container.getBoundingClientRect();
            mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
            mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObjects(nodeMeshes);

            if (intersects.length > 0) {{
                const node = intersects[0].object.userData;
                const sanctionStatus = node.is_sanctioned ?
                    '<span style="color: #ff6666;">SANCTIONED</span>' :
                    '<span style="color: #66b3ff;">Not Sanctioned</span>';
                const addressType = node.is_contract ? 'Contract' : 'EOA';

                nodeInfo.innerHTML = `
                    <strong>${{node.entity || 'Unknown Entity'}}</strong><br>
                    <small>${{node.address.substring(0, 10)}}...</small><br>
                    <strong>Type:</strong> ${{addressType}}<br>
                    <strong>Status:</strong> ${{sanctionStatus}}
                `;
                nodeInfo.classList.add('active');
            }} else {{
                nodeInfo.classList.remove('active');
            }}
        }});

        // Animation loop
        function animate() {{
            requestAnimationFrame(animate);
            applyForces();
            controls.update();
            renderer.render(scene, camera);
        }}

        animate();

        // Control functions
        function resetCamera() {{
            camera.position.set(0, 0, 30);
            controls.reset();
        }}

        function toggleAnimation() {{
            animating = !animating;
        }}

        // Handle window resize
        window.addEventListener('resize', () => {{
            camera.aspect = container.clientWidth / container.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(container.clientWidth, container.clientHeight);
        }});
    </script>
</body>
</html>"""

        return html


if __name__ == "__main__":
    # Test the visualizer
    visualizer = IncidentVisualizer()

    test_incident = {
        "id": "test-001",
        "name": "Test Incident",
        "description": "Test incident for visualization",
        "blockchain": "ethereum"
    }

    test_network = {
        "nodes": [
            {"address": "0x123", "entity": "Entity 1", "risk_score": 80},
            {"address": "0x456", "entity": "Entity 2", "risk_score": 40}
        ],
        "edges": [
            {"source": "0x123", "target": "0x456", "volume": 10000}
        ]
    }

    test_risk = {
        "risk_score": 75,
        "risk_level": "high"
    }

    output_path = "output/test-001/incident.html"
    visualizer.generate_html(test_incident, test_network, test_risk, output_path)
    print(f"Test visualization generated at {output_path}")
