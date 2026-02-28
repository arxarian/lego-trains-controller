import networkx as nx
from pathlib import Path
import filecmp

import python.network_generator as net
import python.models.project_storage as project
from python.items.rail import Rail

IN_GRAPH = "tests/in_graph.dot"
OUT_GRAPH = "tests/out_graph.dot"

def test_load_file():
    data = project.loadDataFromFile(Path("tests/rails_big.json"))
    assert data and len(data) > 0

def test_generate_graph():
    data = project.loadDataFromFile(Path("tests/rails_big.json"))
    assert data and len(data) > 0

    raw_rails = data.get("rails", [])
    rails = [Rail.load_data(d) for d in raw_rails]
    assert len(rails) > 0

    network = net.NetworkGenerator()
    # Full graph (no simplification) for exact dot comparison
    graph = network.generate(rails, simplify=False)

    nx.nx_pydot.write_dot(graph, OUT_GRAPH)

    assert filecmp.cmp(IN_GRAPH, OUT_GRAPH, shallow=False)

    # check if only nodes with A are marked as markers
    for node in graph.nodes():
        if not graph.nodes[node].get("marker", False):
            assert "-" in node
        else:
            assert "A" in node or "B" in node

def test_generate_graph_simplified():
    """Simplified graph contains only marker and switch-adjacent nodes."""
    data = project.loadDataFromFile(Path("tests/rails_big.json"))
    assert data and len(data) > 0

    raw_rails = data.get("rails", [])
    rails = [Rail.load_data(d) for d in raw_rails]
    assert len(rails) > 0

    network = net.NetworkGenerator()
    graph = network.generate(rails, simplify=True)

    for node in graph.nodes():
        data = graph.nodes[node]
        assert data.get("marker") or data.get("at_switch"), (
            f"Simplified graph should only have important nodes, got {node!r} with {data}"
        )
    # Simplified graph should have fewer nodes than full graph
    full_graph = network.generate(rails, simplify=False)
    assert graph.number_of_nodes() <= full_graph.number_of_nodes()
    assert graph.number_of_edges() <= full_graph.number_of_edges()
