from pathlib import Path
from unittest.mock import MagicMock

import pytest
from PySide6.QtWidgets import QApplication

import python.models.project_storage as project
import python.network_manager as net
from python.items.rail import Rail
from python.planner import Planner

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


def test_compute_leg_same_node_is_trivial():
    planner, network = _planner_from_track(TEST_TRACK)
    node = network.find_node_by_color("#ffff00")
    assert node

    leg = planner.compute_leg(node, node)
    assert leg is not None
    assert leg.nodes == [node]
    assert leg.segments == []
    assert leg.length == 0.0


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
