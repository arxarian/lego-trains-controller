from pathlib import Path
from unittest.mock import MagicMock

import networkx as nx
import pytest
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication

import python.models.project_storage as project
import python.network_manager as net
from python.connectorregister import ConnectorRegister
from python.items.marker import MarkerState
from python.items.rail import Rail, RailType
from python.models.rails import Rails
from python.planner import Planner, RequiredSwitch, collect_required_switches

TEST_TRACK = "tests/tracks/rails.json"


@pytest.fixture(scope="session", autouse=True)
def ensure_qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def _planner_from_track(path: str):
    data = project.loadDataFromFile(Path(path))
    rails = [Rail.load_data(d) for d in data.get("rails", [])]
    mock_rails = MagicMock()
    mock_rails.items.return_value = rails
    mock_rails.findRailData.side_effect = (
        lambda rail_id: next((r for r in rails if r.id == int(rail_id)), None)
    )
    network = net.NetworkManager(mock_rails)
    network.generate()
    return Planner(mock_rails, network), network


def _make_switch_y_layout():
    """Straight approach into SwitchLeft with two straight exits (A and B)."""
    rails = Rails(ConnectorRegister())
    rails._items = [
        Rail(type=RailType.Straight, id=1, parent=rails),
        Rail(type=RailType.SwitchLeft, id=2, parent=rails),
        Rail(type=RailType.Straight, id=3, parent=rails),
        Rail(type=RailType.Straight, id=4, parent=rails),
    ]
    approach, switch, exit_a, exit_b = rails._items
    approach.connectTo(switch.id, 1)
    switch.connectTo(approach.id, 0)
    switch.connectTo(exit_a.id, 2)  # end_straight / path A
    exit_a.connectTo(switch.id, 0)
    switch.connectTo(exit_b.id, 1)  # end_curved / path B
    exit_b.connectTo(switch.id, 0)
    return rails, switch


def _force_take(rail, distance, color, path_id=None):
    marker = next(
        m for m in rail.markers._items
        if m.distance == distance and (path_id is None or m.path_id in (None, "", path_id))
    )
    marker.set_color(QColor(color))
    marker.set_state(MarkerState.Taken)
    return marker


def _planner_from_switch_y_with_markers():
    rails, switch = _make_switch_y_layout()
    approach, _switch_rail, exit_a, exit_b = rails._items
    _force_take(approach, 8, "#ff0000")
    _force_take(exit_a, 8, "#00ff00")
    _force_take(exit_b, 8, "#0000ff")
    network = net.NetworkManager(rails)
    network.generate()
    return Planner(rails, network), network, switch


def test_compute_leg_shortest_path_between_markers():
    planner, network = _planner_from_track(TEST_TRACK)
    from_node = network.find_node_by_color("#ffff00")
    to_node = network.find_node_by_color("#ff0000")
    assert from_node and to_node

    leg = planner.compute_leg(from_node, to_node)
    assert leg is not None
    assert leg.nodes[0] == from_node
    assert leg.nodes[-1] == to_node
    assert len(leg.segments) > 0
    for segment_id in leg.segments:
        assert segment_id in network.segments()

    assert leg.nodes == ["6A8", "10A0", "13A0"]
    assert leg.segments == ["10A0:6A8", "10A0:13A0"]
    assert leg.length == 104
    assert leg.required_switches == ()


def test_compute_leg_same_node_is_trivial():
    planner, network = _planner_from_track(TEST_TRACK)
    node = network.find_node_by_color("#ffff00")
    assert node

    leg = planner.compute_leg(node, node)
    assert leg is not None
    assert leg.nodes == [node]
    assert leg.segments == []
    assert leg.length == 0.0
    assert leg.required_switches == ()


def test_compute_leg_unknown_node_returns_none():
    planner, network = _planner_from_track(TEST_TRACK)
    known = network.find_node_by_color("#ffff00")
    assert known

    assert planner.compute_leg(known, "no-such-node") is None
    assert planner.compute_leg("no-such-node", known) is None


def test_compute_leg_no_graph_returns_none():
    mock_rails = MagicMock()
    mock_rails.items.return_value = []
    network = net.NetworkManager(mock_rails)
    planner = Planner(mock_rails, network)

    assert planner.compute_leg("a", "b") is None


def test_compute_leg_curved_branch_requires_switch_path_b():
    planner, network, switch = _planner_from_switch_y_with_markers()
    approach = network.find_node_by_color("#ff0000")
    exit_b = network.find_node_by_color("#0000ff")
    assert approach and exit_b

    leg = planner.compute_leg(approach, exit_b)
    assert leg is not None
    assert leg.required_switches == (RequiredSwitch(rail_id=switch.id, path_id="B"),)
    assert all(rs.rail_id == switch.id for rs in leg.required_switches)


def test_compute_leg_straight_branch_requires_switch_path_a():
    planner, network, switch = _planner_from_switch_y_with_markers()
    approach = network.find_node_by_color("#ff0000")
    exit_a = network.find_node_by_color("#00ff00")
    assert approach and exit_a

    leg = planner.compute_leg(approach, exit_a)
    assert leg is not None
    assert leg.required_switches == (RequiredSwitch(rail_id=switch.id, path_id="A"),)


def test_collect_required_switches_conflict_returns_none():
    """Same switch rail with two path_ids on one path is an invalid leg."""
    rails, switch = _make_switch_y_layout()
    graph = nx.Graph()
    graph.add_edge(
        "n0",
        "n1",
        segment_data=[{"rail_id": switch.id, "path_id": "A", "from": 0, "to": 16}],
    )
    graph.add_edge(
        "n1",
        "n2",
        segment_data=[{"rail_id": switch.id, "path_id": "B", "from": 0, "to": 16}],
    )

    assert collect_required_switches(rails, graph, ["n0", "n1", "n2"]) is None
