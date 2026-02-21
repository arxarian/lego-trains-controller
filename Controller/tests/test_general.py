import networkx as nx
from pathlib import Path
import filecmp

import python.network as net
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

    network = net.Network()
    graph = network.generate(rails)

    nx.nx_pydot.write_dot(graph, OUT_GRAPH)

    assert filecmp.cmp(IN_GRAPH, OUT_GRAPH, shallow=False)

