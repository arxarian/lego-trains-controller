"""B2.1 Stop button pause/resume with previous speed."""

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
from python.planner import Planner

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


def _manual_train():
    network = MagicMock()
    network.find_node_by_color.return_value = None
    device = TrainDeviceSim(name="manual")
    return Train(device, network), device


def test_manual_stop_restores_positive_speed():
    train, device = _manual_train()
    device.set_speed(40)
    assert train.control_mode == ControlMode.Manual

    train.toggle_stop()
    assert device.speed == 0
    assert train.halted_by_stop
    assert train.control_mode == ControlMode.Manual
    assert train.executor is None

    train.toggle_stop()
    assert device.speed == 40
    assert not train.halted_by_stop
    assert train.control_mode == ControlMode.Manual


def test_manual_stop_restores_negative_speed():
    train, device = _manual_train()
    device.set_speed(-40)

    train.toggle_stop()
    assert device.speed == 0
    assert train.halted_by_stop

    train.toggle_stop()
    assert device.speed == -40
    assert not train.halted_by_stop
    assert train.control_mode == ControlMode.Manual


def test_manual_slider_clears_halted_state():
    train, device = _manual_train()
    device.set_speed(40)
    train.toggle_stop()
    assert train.halted_by_stop
    assert device.speed == 0

    device.set_speed(50)
    assert not train.halted_by_stop
    assert device.speed == 50
    assert train.control_mode == ControlMode.Manual


def test_auto_stop_pauses_and_resumes_same_order():
    planner, network = _planner_from_track(TEST_TRACK)
    yellow = network.find_node_by_color(YELLOW)
    red = network.find_node_by_color(RED)
    leg = planner.compute_leg(yellow, red)

    train, device = _auto_train(planner, network)
    device.set_speed(40)
    train.set_current_node_id(yellow)
    train.add_order(red, 0.0)
    train.add_order(yellow, 0.0)
    train.set_control_mode(ControlMode.Automatic)
    assert train.executor.status == ExecutorState.MOVING
    assert train.current_order_index == 0
    assert network.owner_of(leg.segments[0]) == device.name

    train.toggle_stop()
    assert train.control_mode == ControlMode.Automatic
    assert train.halted_by_stop
    assert train.executor.status == ExecutorState.PAUSED
    assert device.speed == 0
    assert train.orders.count == 2
    assert train.current_order_index == 0
    assert network.owner_of(leg.segments[0]) is None

    train.toggle_stop()
    assert train.control_mode == ControlMode.Automatic
    assert not train.halted_by_stop
    assert train.executor.status == ExecutorState.MOVING
    assert abs(device.speed) == 40
    assert train.current_order_index == 0
    assert train.orders.count == 2
    assert network.owner_of(leg.segments[0]) == device.name


def test_auto_stop_resume_uses_fallback_cruise_when_none():
    planner, network = _planner_from_track(TEST_TRACK)
    yellow = network.find_node_by_color(YELLOW)
    red = network.find_node_by_color(RED)

    train, device = _auto_train(planner, network)
    train.set_current_node_id(yellow)
    train.add_order(red, 0.0)
    train.set_control_mode(ControlMode.Automatic)
    assert abs(device.speed) == FALLBACK_SPEED

    train.toggle_stop()
    assert device.speed == 0
    assert train.control_mode == ControlMode.Automatic

    train.toggle_stop()
    assert abs(device.speed) == FALLBACK_SPEED
    assert train.executor.status == ExecutorState.MOVING


def test_auto_stop_during_wait_resumes_toward_next_order():
    planner, network, _switch = _planner_from_switch_y_with_markers()
    start = network.find_node_by_color("#ff0000")
    dest = network.find_node_by_color("#00ff00")
    assert start and dest

    train, device = _auto_train(planner, network)
    device.set_speed(40)
    train.set_current_node_id(start)
    train.add_order(dest, 5.0)
    train.add_order(start, 0.0)
    train.set_control_mode(ControlMode.Automatic)
    assert train.executor.status == ExecutorState.MOVING
    assert train.current_order_index == 0

    async def scenario():
        device.set_color(QColor("#00ff00"))
        assert train.current_node_id == dest
        assert train.executor.status == ExecutorState.WAITING
        assert train.current_order_index == 0

        train.toggle_stop()
        assert train.control_mode == ControlMode.Automatic
        assert train.halted_by_stop
        assert train.executor.status == ExecutorState.PAUSED
        assert device.speed == 0
        assert train.current_order_index == 0
        assert train.orders.count == 2

        train.toggle_stop()
        assert train.control_mode == ControlMode.Automatic
        assert not train.halted_by_stop
        assert train.current_order_index == 1
        assert train.executor.status == ExecutorState.MOVING
        assert abs(device.speed) == 40
        assert train.orders.count == 2

    asyncio.run(scenario())


def test_auto_stop_resume_stays_waiting_for_localization():
    planner, network = _planner_from_track(TEST_TRACK)
    red = network.find_node_by_color(RED)

    train, device = _auto_train(planner, network)
    train.add_order(red, 0.0)
    train.set_control_mode(ControlMode.Automatic)
    assert train.executor.status == ExecutorState.WAITING_FOR_LOCALIZATION
    assert device.speed == 0

    train.toggle_stop()
    assert train.halted_by_stop
    assert train.control_mode == ControlMode.Automatic
    assert train.executor.status == ExecutorState.PAUSED
    assert device.speed == 0

    train.toggle_stop()
    assert not train.halted_by_stop
    assert train.control_mode == ControlMode.Automatic
    assert train.executor.status == ExecutorState.WAITING_FOR_LOCALIZATION
    assert device.speed == 0


def test_mode_switch_does_not_set_halted_by_stop():
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

    train.set_control_mode(ControlMode.Manual)
    assert train.executor.status == ExecutorState.PAUSED
    assert not train.halted_by_stop
    assert network.owner_of(leg.segments[0]) is None
    assert train.orders.count == 2
    assert train.current_order_index == 0
