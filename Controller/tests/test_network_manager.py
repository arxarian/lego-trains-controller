#import networkx as nx
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from PySide6.QtWidgets import QApplication

import python.network_manager as net
import python.models.project_storage as project
from python.items.rail import Rail, RailType
from python.models.rails import Rails
from python.connectorregister import ConnectorRegister

TEST_TRACK = "tests/tracks/rails.json"


@pytest.fixture(scope="session", autouse=True)
def ensure_qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def test_generate_segments():
    data = project.loadDataFromFile(Path(TEST_TRACK))
    assert data and len(data) > 0

    raw_rails = data.get("rails", [])
    rails = [Rail.load_data(d) for d in raw_rails]
    assert len(rails) > 0

    mock_rails = MagicMock()
    mock_rails.items.return_value = rails

    net_manager = net.NetworkManager(mock_rails)
    net_manager.generate()

    assert len(net_manager.segments()) == 5

    assert net_manager.reserve("3A16:6A8")  # test existing segment
    assert not net_manager.reserve("XXX")   # test non-existing segment


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


def test_find_segment_by_entry_node_uses_switch_position():
    rails, switch = _make_switch_y_layout()
    net_manager = net.NetworkManager(rails)
    net_manager.generate()

    entry = "1-2"
    segment_a = "1-2:2-3"
    segment_b = "1-2:2-4"

    assert switch.switch_position == "A"
    assert net_manager.find_segment_by_entry_node(entry) == segment_a

    switch.setSwitchPosition("B")
    assert net_manager.find_segment_by_entry_node(entry) == segment_b

    switch.setSwitchPosition("A")
    assert net_manager.find_segment_by_entry_node(entry) == segment_a

    assert segment_a != segment_b
