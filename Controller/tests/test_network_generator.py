import networkx as nx
from pathlib import Path
import filecmp

import python.network_generator as net
import python.models.project_storage as project
from python.items.rail import Rail

EXPECTED_GRAPH = "tests/data/expected_graph.dot"
ACTUAL_GRAPH = "tests/data/actual_graph.dot"
TEST_TRACK = "tests/tracks/rails_big.json"

def test_generate_graph():
    data = project.loadDataFromFile(Path(TEST_TRACK))
    assert data and len(data) > 0

    raw_rails = data.get("rails", [])
    rails = [Rail.load_data(d) for d in raw_rails]
    assert len(rails) > 0

    network = net.NetworkGenerator()
    # Full graph (no simplification) for exact dot comparison
    graph, nodeMarkerMap = network.generate(rails, simplify=False)

    assert len(nodeMarkerMap) == 40

    nx.nx_pydot.write_dot(graph, ACTUAL_GRAPH)

    assert filecmp.cmp(EXPECTED_GRAPH, ACTUAL_GRAPH, shallow=False)

    # check if only nodes with A are marked as markers
    for node in graph.nodes():
        if not graph.nodes[node].get("marker", False):
            assert "-" in node
        else:
            assert "A" in node or "B" in node

def test_generate_graph_simplified():
    """Simplified graph contains only marker and switch-adjacent nodes."""
    data = project.loadDataFromFile(Path(TEST_TRACK))
    assert data and len(data) > 0

    raw_rails = data.get("rails", [])
    rails = [Rail.load_data(d) for d in raw_rails]
    assert len(rails) > 0

    network = net.NetworkGenerator()
    graph, nodeMarkerMap = network.generate(rails, simplify=True)

    assert len(nodeMarkerMap) == 40

    for node in graph.nodes():
        data = graph.nodes[node]
        assert data.get("marker") or data.get("at_switch"), (
            f"Simplified graph should only have important nodes, got {node!r} with {data}"
        )
    # Simplified graph should have fewer nodes than full graph
    full_graph, nodeMarkerMap = network.generate(rails, simplify=False)
    assert graph.number_of_nodes() <= full_graph.number_of_nodes()
    assert graph.number_of_edges() <= full_graph.number_of_edges()
