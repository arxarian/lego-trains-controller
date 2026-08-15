"""Plan executor state machine (B1.2).

Drive Auto progress by injecting colors on TrainDeviceSim.set_color.
The live Simulator still walks the full marker circuit (S2 will follow reserved legs).
"""

import asyncio
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication

import python.models.project_storage as project
import python.network_manager as net
from python.connectorregister import ConnectorRegister
from python.items.marker import MarkerState
from python.items.rail import Rail, RailType
from python.items.train import ControlMode, Train
from python.items.train_device_sim import TrainDeviceSim
from python.models.rails import Rails
from python.plan_executor import ExecutorState, FALLBACK_SPEED
from python.planner import LegResult, Planner

TEST_TRACK = "tests/tracks/rails.json"
YELLOW = "#ffff00"
RED = "#ff0000"


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


def _auto_train(planner, network, name="auto"):
    device = TrainDeviceSim(name=name)
    train = Train(device, network, planner)
    return train, device


def test_two_waypoints_free_track_moves_waits_and_loops():
    # Dead-end markers: A→B→A must reverse at each end, which the executor allows.
    planner, network, _switch = _planner_from_switch_y_with_markers()
    start = network.find_node_by_color("#ff0000")
    dest = network.find_node_by_color("#00ff00")
    assert start and dest

    train, device = _auto_train(planner, network)
    train.set_current_node_id(start)
    train.add_order(dest, 0.0)
    train.add_order(start, 0.0)
    train.set_control_mode(ControlMode.Automatic)

    assert train.executor.status == ExecutorState.MOVING
    assert device.speed > 0
    leg = planner.compute_leg(start, dest)
    assert all(network.owner_of(sid) == device.name for sid in leg.segments)

    device.set_color(QColor("#00ff00"))
    assert train.current_node_id == dest
    assert train.current_order_index == 1
    assert train.executor.status == ExecutorState.MOVING
    assert device.speed != 0
    back = planner.compute_leg(dest, start)
    assert all(network.owner_of(sid) == device.name for sid in back.segments)


def test_overlapping_leg_holds_until_free():
    planner, network = _planner_from_track(TEST_TRACK)
    yellow = network.find_node_by_color(YELLOW)
    red = network.find_node_by_color(RED)
    leg = planner.compute_leg(yellow, red)
    assert network.try_reserve_leg("blocker", [leg.segments[0]])

    train, device = _auto_train(planner, network)
    train.set_current_node_id(yellow)
    train.add_order(red, 0.0)
    train.set_control_mode(ControlMode.Automatic)

    assert train.executor.status == "Hold: conflict"
    assert device.speed == 0
    assert network.owner_of(leg.segments[0]) == "blocker"

    network.release_leg("blocker", [leg.segments[0]])
    train.executor.try_depart()
    assert train.executor.status == ExecutorState.MOVING
    assert device.speed > 0
    assert network.owner_of(leg.segments[0]) == device.name


def test_hold_retry_moves_when_leg_frees():
    planner, network = _planner_from_track(TEST_TRACK)
    yellow = network.find_node_by_color(YELLOW)
    red = network.find_node_by_color(RED)
    leg = planner.compute_leg(yellow, red)
    assert network.try_reserve_leg("blocker", [leg.segments[0]])

    train, device = _auto_train(planner, network)
    train.executor._hold_retry_s = 0.02
    train.set_current_node_id(yellow)
    train.add_order(red, 0.0)

    async def scenario():
        train.set_control_mode(ControlMode.Automatic)
        assert train.executor.status == "Hold: conflict"
        network.release_leg("blocker", [leg.segments[0]])
        await asyncio.sleep(0.06)
        assert train.executor.status == ExecutorState.MOVING
        assert device.speed > 0

    asyncio.run(scenario())


def _planner_from_linear_three_markers():
    """Three connected straights — middle marker has two neighbors, no loop."""
    rails = Rails(ConnectorRegister())
    rails._items = [
        Rail(type=RailType.Straight, id=1, parent=rails),
        Rail(type=RailType.Straight, id=2, parent=rails),
        Rail(type=RailType.Straight, id=3, parent=rails),
    ]
    a, b, c = rails._items
    a.connectTo(b.id, 1)
    b.connectTo(a.id, 0)
    b.connectTo(c.id, 1)
    c.connectTo(b.id, 0)
    _force_take(a, 8, "#ff0000")
    _force_take(b, 8, "#00ff00")
    _force_take(c, 8, "#0000ff")
    network = net.NetworkManager(rails)
    network.generate()
    return Planner(rails, network), network


def test_non_dead_end_reverse_holds():
    planner, network = _planner_from_linear_three_markers()
    red = network.find_node_by_color("#ff0000")
    green = network.find_node_by_color("#00ff00")
    assert red and green
    assert network.graph().degree(green) > 1

    train, device = _auto_train(planner, network)
    train.set_current_node_id(green)
    train.executor.set_previous_node_id(red)
    train.add_order(red, 0.0)
    train.set_control_mode(ControlMode.Automatic)

    assert train.executor.status == "Hold: no reverse"
    assert device.speed == 0


def test_allow_reverse_departs_when_no_forward_path():
    planner, network = _planner_from_linear_three_markers()
    red = network.find_node_by_color("#ff0000")
    green = network.find_node_by_color("#00ff00")

    train, device = _auto_train(planner, network)
    device.set_speed(40)
    train.set_allow_reverse(True)
    train.set_current_node_id(green)
    train.executor.set_previous_node_id(red)
    train.add_order(red, 0.0)
    train.set_control_mode(ControlMode.Automatic)

    assert train.executor.status == ExecutorState.MOVING
    assert device.speed == -40


def test_oval_two_stops_loop_forward_without_reverse():
    planner, network = _planner_from_track(TEST_TRACK)
    blue = network.find_node_by_color("#0000ff")
    red = network.find_node_by_color(RED)
    assert blue == "10A0"
    assert red == "13A0"

    train, device = _auto_train(planner, network)
    device.set_speed(40)
    train.set_current_node_id(blue)
    train.add_order(red, 0.0)
    train.add_order(blue, 0.0)
    train.set_control_mode(ControlMode.Automatic)

    assert train.executor.status == ExecutorState.MOVING
    assert device.speed > 0

    device.set_color(QColor(RED))
    assert train.current_node_id == red
    assert train.executor.status == ExecutorState.MOVING
    assert device.speed != 0
    assert train.executor.status != "Hold: no reverse"
    forward = planner.compute_leg(red, blue, exclude_neighbor=blue)
    assert all(network.owner_of(sid) == device.name for sid in forward.segments)


def test_allow_reverse_uses_shortest_path_even_if_reverse():
    planner, network = _planner_from_track(TEST_TRACK)
    blue = network.find_node_by_color("#0000ff")
    red = network.find_node_by_color(RED)
    assert blue == "10A0"
    assert red == "13A0"

    train, device = _auto_train(planner, network)
    device.set_speed(40)
    train.set_allow_reverse(True)
    train.set_current_node_id(red)
    train.executor.set_previous_node_id(blue)
    train.add_order(blue, 0.0)
    train.set_control_mode(ControlMode.Automatic)

    assert train.executor.status == ExecutorState.MOVING
    assert device.speed == -40
    short = planner.compute_leg(red, blue)
    assert short.nodes[1] == blue
    assert train.current_segment_id == f"{red}:{blue}"
    assert all(network.owner_of(sid) == device.name for sid in short.segments)


def test_dead_end_reverse_allowed_flips_signed_speed():
    planner, network, _switch = _planner_from_switch_y_with_markers()
    approach = network.find_node_by_color("#ff0000")
    exit_a = network.find_node_by_color("#00ff00")
    assert approach and exit_a
    assert network.is_dead_end(approach)

    train, device = _auto_train(planner, network)
    device.set_speed(40)
    train.set_current_node_id(approach)
    train.executor.set_previous_node_id("1-2")
    train.add_order(exit_a, 0.0)
    train.set_control_mode(ControlMode.Automatic)

    assert train.executor.status == ExecutorState.MOVING
    assert device.speed == -40


def test_forward_depart_keeps_cruise_sign():
    planner, network = _planner_from_track(TEST_TRACK)
    yellow = network.find_node_by_color(YELLOW)
    red = network.find_node_by_color(RED)

    train, device = _auto_train(planner, network)
    device.set_speed(-30)
    train.set_current_node_id(yellow)
    train.add_order(red, 0.0)
    train.set_control_mode(ControlMode.Automatic)

    assert train.executor.status == ExecutorState.MOVING
    assert device.speed == -30


def test_fallback_speed_when_last_speed_is_zero():
    planner, network = _planner_from_track(TEST_TRACK)
    yellow = network.find_node_by_color(YELLOW)
    red = network.find_node_by_color(RED)

    train, device = _auto_train(planner, network)
    device.set_speed(0)
    train.set_current_node_id(yellow)
    train.add_order(red, 0.0)
    train.set_control_mode(ControlMode.Automatic)

    assert train.executor.status == ExecutorState.MOVING
    assert device.speed == FALLBACK_SPEED


def test_live_speed_survives_wait0_arrive():
    planner, network, _switch = _planner_from_switch_y_with_markers()
    start = network.find_node_by_color("#ff0000")
    dest = network.find_node_by_color("#00ff00")
    assert start and dest

    train, device = _auto_train(planner, network)
    device.set_speed(40)
    train.set_current_node_id(start)
    train.add_order(dest, 0.0)
    train.add_order(start, 0.0)
    train.set_control_mode(ControlMode.Automatic)

    assert train.executor.status == ExecutorState.MOVING
    assert abs(device.speed) == 40

    device.set_speed(80 if device.speed > 0 else -80)
    device.set_color(QColor("#00ff00"))
    assert train.current_node_id == dest
    assert train.executor.status == ExecutorState.MOVING
    assert abs(device.speed) == 80


def test_positive_wait_stops_then_departs():
    planner, network, _switch = _planner_from_switch_y_with_markers()
    start = network.find_node_by_color("#ff0000")
    dest = network.find_node_by_color("#00ff00")
    assert start and dest

    train, device = _auto_train(planner, network)
    train.executor._hold_retry_s = 0.02
    device.set_speed(40)
    train.set_current_node_id(start)
    train.add_order(dest, 0.05)
    train.add_order(start, 0.0)

    async def scenario():
        train.set_control_mode(ControlMode.Automatic)
        assert train.executor.status == ExecutorState.MOVING
        device.set_color(QColor("#00ff00"))
        assert train.executor.status == ExecutorState.WAITING
        assert device.speed == 0
        await asyncio.sleep(0.08)
        assert train.executor.status == ExecutorState.MOVING
        assert abs(device.speed) == 40

    asyncio.run(scenario())


def test_pause_releases_leg_and_keeps_orders():
    planner, network = _planner_from_track(TEST_TRACK)
    yellow = network.find_node_by_color(YELLOW)
    red = network.find_node_by_color(RED)
    leg = planner.compute_leg(yellow, red)

    train, device = _auto_train(planner, network)
    train.set_current_node_id(yellow)
    train.add_order(red, 0.0)
    train.add_order(yellow, 0.0)
    train.set_control_mode(ControlMode.Automatic)
    assert train.executor.status == ExecutorState.MOVING
    assert network.owner_of(leg.segments[0]) == device.name

    train.set_control_mode(ControlMode.Manual)
    assert train.executor.status == ExecutorState.PAUSED
    assert network.owner_of(leg.segments[0]) is None
    assert train.orders.count == 2
    assert train.current_order_index == 0
    assert train.current_node_id == yellow


def test_auto_color_does_not_use_marker_occupancy():
    network = MagicMock()
    network.find_node_by_color.return_value = "n1"
    network.try_reserve_leg.return_value = True
    network.is_reverse_depart.return_value = False
    network.is_dead_end.return_value = False
    planner = MagicMock()
    planner.compute_leg.return_value = LegResult(nodes=["n1", "n2"], segments=["n1:n2"], length=1.0)

    device = TrainDeviceSim(name="mock")
    train = Train(device, network, planner)
    train.set_current_node_id("n0")
    train.add_order("n2", 0.0)
    train.set_control_mode(ControlMode.Automatic)

    device.set_color(QColor("#ff0000"))
    network.walk_to_next_marker.assert_not_called()
    network.try_reserve_segment.assert_not_called()
    assert train.current_node_id == "n1"


def test_waits_for_localization_before_depart():
    planner, network = _planner_from_track(TEST_TRACK)
    yellow = network.find_node_by_color(YELLOW)
    red = network.find_node_by_color(RED)

    train, device = _auto_train(planner, network)
    train.add_order(red, 0.0)
    train.set_control_mode(ControlMode.Automatic)
    assert train.executor.status == ExecutorState.WAITING_FOR_LOCALIZATION
    assert device.speed == 0

    device.set_color(QColor(YELLOW))
    assert train.current_node_id == yellow
    assert train.executor.status == ExecutorState.MOVING
    assert device.speed > 0


def test_is_reverse_depart_helper():
    planner, network = _planner_from_track(TEST_TRACK)
    yellow = network.find_node_by_color(YELLOW)
    red = network.find_node_by_color(RED)
    leg = planner.compute_leg(red, yellow)
    assert not network.is_dead_end(red)
    assert network.is_reverse_depart(red, yellow, leg.nodes[1])
    assert not network.is_reverse_depart(red, None, leg.nodes[1])

    y_planner, y_network, _ = _planner_from_switch_y_with_markers()
    approach = y_network.find_node_by_color("#ff0000")
    exit_a = y_network.find_node_by_color("#00ff00")
    y_leg = y_planner.compute_leg(approach, exit_a)
    assert y_network.is_dead_end(approach)
    assert not y_network.is_reverse_depart(approach, "1-2", y_leg.nodes[1])
