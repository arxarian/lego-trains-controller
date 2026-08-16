import pytest
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication

import python.network_manager as net
from python.connectorregister import ConnectorRegister
from python.items.marker import MarkerState
from python.items.rail import Rail, RailType
from python.models.rails import Rails
from python.planner import Planner


@pytest.fixture(scope="session", autouse=True)
def ensure_qapp():
    app = QApplication.instance() or QApplication([])
    yield app


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
    switch.connectTo(exit_a.id, 2)
    exit_a.connectTo(switch.id, 0)
    switch.connectTo(exit_b.id, 1)
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


def test_reserve_leg_sets_path_b_and_blocks_toggle():
    planner, network, switch = _planner_from_switch_y_with_markers()
    approach = network.find_node_by_color("#ff0000")
    exit_b = network.find_node_by_color("#0000ff")
    leg = planner.compute_leg(approach, exit_b)
    assert leg is not None

    assert network.try_reserve_leg("train-a", leg.segments)
    assert switch.switch_position == "B"
    assert switch.path_indicators.path_id_active == "B"
    assert switch.locked
    assert switch.locked_by == "train-a"

    switch.toggleSwitchPosition()
    assert switch.switch_position == "B"


def test_release_leg_unlocks_and_manual_toggle_works():
    planner, network, switch = _planner_from_switch_y_with_markers()
    approach = network.find_node_by_color("#ff0000")
    exit_b = network.find_node_by_color("#0000ff")
    leg = planner.compute_leg(approach, exit_b)
    assert leg is not None

    assert network.try_reserve_leg("train-a", leg.segments)
    assert network.release_leg("train-a", leg.segments)
    assert not switch.locked
    assert switch.locked_by == ""

    switch.toggleSwitchPosition()
    assert switch.switch_position == "A"


def test_foreign_switch_lock_fails_atomically():
    planner, network, switch = _planner_from_switch_y_with_markers()
    approach = network.find_node_by_color("#ff0000")
    exit_a = network.find_node_by_color("#00ff00")
    leg = planner.compute_leg(approach, exit_a)
    assert leg is not None

    switch.set_switch_position("B")
    switch.lock_for("train-a")

    assert not network.try_reserve_leg("train-b", leg.segments)
    assert all(network.owner_of(sid) is None for sid in leg.segments)
    assert switch.switch_position == "B"
    assert switch.locked_by == "train-a"


def test_same_owner_rereserve_keeps_lock():
    planner, network, switch = _planner_from_switch_y_with_markers()
    approach = network.find_node_by_color("#ff0000")
    exit_b = network.find_node_by_color("#0000ff")
    leg = planner.compute_leg(approach, exit_b)
    assert leg is not None

    assert network.try_reserve_leg("train-a", leg.segments)
    assert network.try_reserve_leg("train-a", leg.segments)
    assert switch.switch_position == "B"
    assert switch.locked_by == "train-a"


def test_release_all_for_unlocks_owner_switches():
    planner, network, switch = _planner_from_switch_y_with_markers()
    approach = network.find_node_by_color("#ff0000")
    exit_b = network.find_node_by_color("#0000ff")
    leg = planner.compute_leg(approach, exit_b)
    assert leg is not None

    assert network.try_reserve_leg("train-a", leg.segments)
    network.release_all_for("train-a")
    assert not switch.locked
    assert all(network.owner_of(sid) is None for sid in leg.segments)


def test_generate_clears_switch_locks():
    planner, network, switch = _planner_from_switch_y_with_markers()
    approach = network.find_node_by_color("#ff0000")
    exit_b = network.find_node_by_color("#0000ff")
    leg = planner.compute_leg(approach, exit_b)
    assert leg is not None

    assert network.try_reserve_leg("train-a", leg.segments)
    assert switch.locked

    network.generate()
    assert not switch.locked
    assert switch.locked_by == ""
