#import networkx as nx
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication

import python.network_manager as net
import python.models.project_storage as project
from python.items.rail import Rail, RailType
from python.items.marker import MarkerState
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


def _network_from_track(path: str):
    data = project.loadDataFromFile(Path(path))
    rails = [Rail.load_data(d) for d in data.get("rails", [])]
    mock_rails = MagicMock()
    mock_rails.items.return_value = rails
    mock_rails.findRailData.side_effect = (
        lambda rail_id: next((r for r in rails if r.id == int(rail_id)), None)
    )
    net_manager = net.NetworkManager(mock_rails)
    net_manager.generate()
    return net_manager


def test_find_segment_circuit_empty_exclude_falls_back():
    net_manager = _network_from_track(TEST_TRACK)
    neighbors = list(net_manager.graph().neighbors("13A0"))
    possible = {":".join(sorted(["13A0", n])) for n in neighbors}

    segment = net_manager.find_segment_by_entry_node("13A0")
    assert segment is not None
    assert segment in possible

    assert net_manager.find_segment_by_entry_node("13A0", "19A0") == "10A0:13A0"


def _force_take(rail, distance, color, path_id=None):
    marker = next(
        m for m in rail.markers._items
        if m.distance == distance and (path_id is None or m.path_id in (None, "", path_id))
    )
    marker.set_color(QColor(color))
    marker.set_state(MarkerState.Taken)
    return marker


def test_find_next_marker_node_uses_switch_position():
    """From the approach marker, switch A vs B selects different exit markers."""
    rails, switch = _make_switch_y_layout()
    approach, _switch_rail, exit_a, exit_b = rails._items

    _force_take(approach, 8, "#ff0000")
    _force_take(exit_a, 8, "#00ff00")
    _force_take(exit_b, 8, "#0000ff")

    net_manager = net.NetworkManager(rails)
    net_manager.generate()

    approach_node = net_manager.find_node_by_color("#ff0000")
    exit_a_node = net_manager.find_node_by_color("#00ff00")
    exit_b_node = net_manager.find_node_by_color("#0000ff")
    assert approach_node and exit_a_node and exit_b_node

    # After simplify, the approach marker's only neighbor is the switch junction
    # "1-2", so exclude=None walks toward the exits.
    assert list(net_manager.graph().neighbors(approach_node)) == ["1-2"]

    assert switch.switch_position == "A"
    assert net_manager.find_next_marker_node(approach_node) == exit_a_node

    switch.setSwitchPosition("B")
    assert net_manager.find_next_marker_node(approach_node) == exit_b_node

    switch.setSwitchPosition("A")
    assert net_manager.find_next_marker_node(approach_node) == exit_a_node


def test_select_next_node_trailing_allows_inactive_single_candidate():
    """Trailing (one forward hop) ignores switch state; forking still filters."""
    rails, switch = _make_switch_y_layout()
    approach, _switch_rail, exit_a, exit_b = rails._items
    _force_take(approach, 8, "#ff0000")
    _force_take(exit_a, 8, "#00ff00")
    _force_take(exit_b, 8, "#0000ff")

    net_manager = net.NetworkManager(rails)
    net_manager.generate()

    exit_a_node = net_manager.find_node_by_color("#00ff00")
    exit_b_node = net_manager.find_node_by_color("#0000ff")
    stem = "1-2"
    neighbors = list(net_manager.graph().neighbors(stem))
    assert "2-3" in neighbors and "2-4" in neighbors

    assert switch.switch_position == "A"
    assert net_manager._edge_matches_switch_state(stem, "2-4") is False

    # Trailing: sole forward hop from exit-B side node toward stem is allowed
    # even though path B does not match switch A.
    exit_b_neighbors = list(net_manager.graph().neighbors(exit_b_node))
    assert len(exit_b_neighbors) == 1
    assert net_manager._select_next_node(exit_b_node, None) == exit_b_neighbors[0]

    # Forking: exclude approach → must pick A, not B.
    assert net_manager._select_next_node(stem, "1A8") == "2-3"

    # From exit A with switch A, next marker is approach (not exit B).
    assert net_manager.find_next_marker_node(exit_a_node) == "1A8"
    assert net_manager.find_next_marker_node(exit_a_node) != exit_b_node

    switch.setSwitchPosition("B")
    assert net_manager._select_next_node(stem, "1A8") == "2-4"
    assert net_manager.find_next_marker_node(exit_b_node) != exit_a_node


def test_resolve_exclude_neighbor_maps_marker_to_entry_edge():
    """Previous marker that is not adjacent resolves to the arrival neighbor."""
    rails, switch = _make_switch_y_layout()
    approach, _switch_rail, exit_a, exit_b = rails._items
    _force_take(approach, 8, "#ff0000")
    _force_take(exit_a, 8, "#00ff00")
    _force_take(exit_b, 8, "#0000ff")

    net_manager = net.NetworkManager(rails)
    net_manager.generate()

    approach_node = net_manager.find_node_by_color("#ff0000")
    exit_a_node = net_manager.find_node_by_color("#00ff00")
    stem = "1-2"

    # Exit marker's entry edge from approach is junction 2-3.
    entry = None
    prev_map = {approach_node: None}
    queue = [approach_node]
    while queue:
        cur = queue.pop(0)
        for n in net_manager.graph().neighbors(cur):
            if n in prev_map:
                continue
            prev_map[n] = cur
            if n == exit_a_node:
                entry = prev_map[n]
                queue.clear()
                break
            queue.append(n)
    assert entry == "2-3"

    # Dead-end exit: resolve must not exclude the only neighbor (returns None),
    # so the walk can still return toward the approach marker.
    assert net_manager._resolve_exclude_neighbor(exit_a_node, approach_node) is None
    assert switch.switch_position == "A"
    assert net_manager.find_next_marker_node(exit_a_node, approach_node) == approach_node

    # At the stem (deg >= 2), approach resolves to itself as direct neighbor.
    assert net_manager._resolve_exclude_neighbor(stem, approach_node) == approach_node
    # From stem, previous=exit_a resolves to entry edge 2-3 (not a no-op).
    assert net_manager._resolve_exclude_neighbor(stem, exit_a_node) == "2-3"
    # With that exclude, forking picks the other branch / approach correctly.
    assert net_manager._select_next_node(
        stem, net_manager._resolve_exclude_neighbor(stem, exit_a_node)
    ) == "1A8"


def test_trailing_at_stem_never_frog_crosses():
    """Trailing into the stem from one branch continues to approach, not the other exit."""
    rails, switch = _make_switch_y_layout()
    approach, _switch_rail, exit_a, exit_b = rails._items
    _force_take(approach, 8, "#ff0000")
    _force_take(exit_a, 8, "#00ff00")
    _force_take(exit_b, 8, "#0000ff")

    net_manager = net.NetworkManager(rails)
    net_manager.generate()

    stem = "1-2"
    assert net_manager._edge_involves_switch(stem, "2-3")
    assert net_manager._edge_involves_switch(stem, "2-4")
    assert not net_manager._edge_involves_switch(stem, "1A8")

    for path_id in ("A", "B"):
        switch.setSwitchPosition(path_id)
        assert net_manager._select_next_node(stem, "2-3") == "1A8"
        assert net_manager._select_next_node(stem, "2-4") == "1A8"

    # Facing from approach still respects switch position.
    switch.setSwitchPosition("A")
    assert net_manager._select_next_node(stem, "1A8") == "2-3"
    switch.setSwitchPosition("B")
    assert net_manager._select_next_node(stem, "1A8") == "2-4"


def test_find_segments_to_next_marker_covers_switch():
    """Approach → next marker reserves every edge through the junction."""
    rails, switch = _make_switch_y_layout()
    approach, _switch_rail, exit_a, exit_b = rails._items
    _force_take(approach, 8, "#ff0000")
    _force_take(exit_a, 8, "#00ff00")
    _force_take(exit_b, 8, "#0000ff")

    net_manager = net.NetworkManager(rails)
    net_manager.generate()

    approach_node = net_manager.find_node_by_color("#ff0000")
    exit_a_node = net_manager.find_node_by_color("#00ff00")
    exit_b_node = net_manager.find_node_by_color("#0000ff")

    segments_a = net_manager.find_segments_to_next_marker(approach_node)
    assert len(segments_a) >= 2
    assert segments_a[0] == ":".join(sorted([approach_node, "1-2"]))
    assert exit_a_node in segments_a[-1]
    assert net_manager.find_next_marker_node(approach_node) == exit_a_node

    switch.setSwitchPosition("B")
    segments_b = net_manager.find_segments_to_next_marker(approach_node)
    assert len(segments_b) >= 2
    assert segments_b != segments_a
    assert exit_b_node in segments_b[-1]
    assert net_manager.find_next_marker_node(approach_node) == exit_b_node


def test_color_for_node():
    from python.items.marker import Marker

    mock_rails = MagicMock()
    mock_rails.items.return_value = []
    net_manager = net.NetworkManager(mock_rails)

    red = QColor("#ff0000")
    marker = Marker(color=red)
    net_manager._nodeMarkerMap["1A10"] = marker

    assert net_manager.color_for_node("1A10") == red
    assert not net_manager.color_for_node("missing").isValid()
    assert not net_manager.color_for_node("").isValid()
