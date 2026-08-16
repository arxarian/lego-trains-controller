from pathlib import Path
from unittest.mock import MagicMock

import pytest
from PySide6.QtWidgets import QApplication

import python.models.project_storage as project_storage
import python.network_manager as net
from python.items.project import Project
from python.items.rail import Rail
from python.items.train import ControlMode, Train
from python.items.train_device_sim import TrainDeviceSim
from python.models.trains import Trains
from python.plan_executor import ExecutorState
from python.planner import Planner
from python.simulator import Simulator
from python.train_plan import snapshot_train, wait_from_json

TEST_TRACK = "tests/tracks/rails.json"


@pytest.fixture(scope="session", autouse=True)
def ensure_qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def _network_from_track(path: str, *, generate=True):
    data = project_storage.loadDataFromFile(Path(path))
    rails = [Rail.load_data(d) for d in data.get("rails", [])]
    mock_rails = MagicMock()
    mock_rails.items.return_value = rails
    mock_rails.findRailData.side_effect = (
        lambda rail_id: next((r for r in rails if r.id == int(rail_id)), None)
    )
    network = net.NetworkManager(mock_rails)
    if generate:
        network.generate()
    return network, data


def _make_trains(network, planner=None):
    return Trains(network, MagicMock(), planner)


def _planner_for(network):
    return Planner(network._rails, network)


def _simulator_plan(orders, *, control_mode="automatic", allow_reverse=True, current_order_index=1):
    return {
        "key": "Simulator",
        "kind": "sim",
        "control_mode": control_mode,
        "allow_reverse": allow_reverse,
        "current_order_index": current_order_index,
        "orders": orders,
    }


def test_wait_from_json_unknown_type():
    seconds, warning = wait_from_json({"type": "until_other_train"})
    assert seconds == 0.0
    assert warning is not None


def test_old_project_without_trains_loads():
    project = Project("legacy", {"rails": [], "settings": {}})
    assert project.train_plans() == []
    assert project.save_data()["trains"] == []


def test_round_trip_train_plan():
    network, _ = _network_from_track(TEST_TRACK)
    node_ids = network.marker_node_ids()
    assert len(node_ids) >= 2

    device = TrainDeviceSim(name="Simulator")
    train = Train(device, network)
    train.add_order(node_ids[0], 0.0)
    train.add_order(node_ids[1], 5.0)
    train.set_current_order_index(1)
    train.set_allow_reverse(True)
    train.set_control_mode(ControlMode.Automatic)

    project = Project("round")
    project.upsert_train_plan(snapshot_train(train))
    data = project.save_data()

    assert data["trains"][0]["key"] == "Simulator"
    assert data["trains"][0]["kind"] == "sim"
    assert data["trains"][0]["control_mode"] == "automatic"
    assert data["trains"][0]["allow_reverse"] is True
    assert data["trains"][0]["current_order_index"] == 1
    assert data["trains"][0]["orders"][1]["wait"] == {"type": "seconds", "seconds": 5.0}

    loaded = Project("round", data)
    trains = _make_trains(network, _planner_for(network))
    trains.set_project(loaded)
    restored = trains.add_train(TrainDeviceSim(name="Simulator"))

    assert restored.orders.count == 2
    assert restored.orders.get(0).target_node_id == node_ids[0]
    assert restored.orders.get(1).target_node_id == node_ids[1]
    assert restored.orders.get(1).wait_seconds == 5.0
    assert restored.current_order_index == 1
    assert restored.allow_reverse is True
    assert restored.control_mode == ControlMode.Automatic
    assert restored.halted_by_stop
    assert restored.executor.status == ExecutorState.PAUSED

    restored.toggle_stop()
    assert not restored.halted_by_stop
    assert restored.control_mode == ControlMode.Automatic
    assert restored.executor.status != ExecutorState.PAUSED


def test_missing_device_then_attach():
    network, _ = _network_from_track(TEST_TRACK)
    node_ids = network.marker_node_ids()
    plan = _simulator_plan([
        {"target_node_id": node_ids[0], "wait": {"type": "seconds", "seconds": 0}},
        {"target_node_id": node_ids[1], "wait": {"type": "seconds", "seconds": 5}},
    ])
    project = Project("orphan", {"rails": [], "settings": {}, "trains": [plan]})
    trains = _make_trains(network, _planner_for(network))
    trains.set_project(project)

    assert trains.rowCount() == 0
    saved = project.save_data()
    assert saved["trains"][0]["key"] == "Simulator"
    assert len(saved["trains"][0]["orders"]) == 2

    attached = trains.add_train(TrainDeviceSim(name="Simulator"))
    assert attached.orders.count == 2
    assert attached.orders.get(0).target_node_id == node_ids[0]
    assert attached.orders.get(1).wait_seconds == 5.0
    assert attached.control_mode == ControlMode.Automatic
    assert attached.allow_reverse is True
    assert attached.halted_by_stop
    assert attached.executor.status == ExecutorState.PAUSED


def test_stale_node_dropped_after_generate():
    network, _ = _network_from_track(TEST_TRACK, generate=False)
    generated, _ = _network_from_track(TEST_TRACK)
    real_node = generated.marker_node_ids()[0]
    plan = _simulator_plan(
        [
            {"target_node_id": real_node, "wait": {"type": "seconds", "seconds": 0}},
            {"target_node_id": "missingNode", "wait": {"type": "seconds", "seconds": 0}},
        ],
        control_mode="manual",
        allow_reverse=False,
        current_order_index=0,
    )
    project = Project("stale", {"rails": [], "settings": {}, "trains": [plan]})
    trains = _make_trains(network)
    trains.set_project(project)
    train = trains.add_train(TrainDeviceSim(name="Simulator"))

    assert train.orders.count == 2

    network.generate()

    assert train.orders.count == 1
    assert train.orders.get(0).target_node_id == real_node
    assert "missingNode" in trains.last_order_hint

    trains.sync_live_into_project(project)
    saved_orders = project.save_data()["trains"][0]["orders"]
    assert [order["target_node_id"] for order in saved_orders] == [real_node]


def test_stale_node_dropped_on_attach_when_graph_exists():
    network, _ = _network_from_track(TEST_TRACK)
    real_node = network.marker_node_ids()[0]
    plan = _simulator_plan(
        [
            {"target_node_id": real_node, "wait": {"type": "seconds", "seconds": 0}},
            {"target_node_id": "missingNode", "wait": {"type": "seconds", "seconds": 0}},
        ],
        control_mode="manual",
        allow_reverse=False,
        current_order_index=0,
    )
    project = Project("stale-attach", {"rails": [], "settings": {}, "trains": [plan]})
    trains = _make_trains(network)
    trains.set_project(project)
    train = trains.add_train(TrainDeviceSim(name="Simulator"))

    assert train.orders.count == 1
    assert train.orders.get(0).target_node_id == real_node
    assert "missingNode" in trains.last_order_hint
    assert [order["target_node_id"] for order in project.train_plan_for("Simulator")["orders"]] == [real_node]


def test_unknown_wait_type_becomes_zero():
    network, _ = _network_from_track(TEST_TRACK)
    real_node = network.marker_node_ids()[0]
    plan = _simulator_plan(
        [{"target_node_id": real_node, "wait": {"type": "until_other_train"}}],
        control_mode="manual",
        allow_reverse=False,
        current_order_index=0,
    )
    project = Project("wait", {"rails": [], "settings": {}, "trains": [plan]})
    trains = _make_trains(network)
    trains.set_project(project)
    train = trains.add_train(TrainDeviceSim(name="Simulator"))

    assert train.orders.count == 1
    assert train.orders.get(0).wait_seconds == 0.0
    assert "Unknown wait type" in trains.last_order_hint


def test_project_switch_clears_unmatched_train():
    network, _ = _network_from_track(TEST_TRACK)
    node_ids = network.marker_node_ids()
    trains = _make_trains(network)
    first = Project("first", {
        "rails": [],
        "settings": {},
        "trains": [_simulator_plan(
            [{"target_node_id": node_ids[0], "wait": {"type": "seconds", "seconds": 0}}],
            control_mode="manual",
            allow_reverse=False,
            current_order_index=0,
        )],
    })
    trains.set_project(first)
    train = trains.add_train(TrainDeviceSim(name="Simulator"))
    assert train.orders.count == 1

    empty = Project("empty", {"rails": [], "settings": {}})
    trains.set_project(empty)
    assert train.orders.count == 0
    assert train.control_mode == ControlMode.Manual
    assert not train.halted_by_stop


def test_manual_plan_attach_is_not_halted():
    network, _ = _network_from_track(TEST_TRACK)
    node_ids = network.marker_node_ids()
    plan = _simulator_plan(
        [{"target_node_id": node_ids[0], "wait": {"type": "seconds", "seconds": 0}}],
        control_mode="manual",
        allow_reverse=False,
        current_order_index=0,
    )
    project = Project("manual", {"rails": [], "settings": {}, "trains": [plan]})
    trains = _make_trains(network, _planner_for(network))
    trains.set_project(project)
    train = trains.add_train(TrainDeviceSim(name="Simulator"))

    assert train.control_mode == ControlMode.Manual
    assert not train.halted_by_stop
    assert train.executor.status == ExecutorState.PAUSED


def test_simulator_starts_parked_at_zero_speed():
    network, _ = _network_from_track(TEST_TRACK)
    trains = _make_trains(network, _planner_for(network))
    sim = Simulator(network, trains)
    sim.start()

    assert sim.is_running
    assert sim._sim_device.speed == 0
    assert sim._run_task is None
    assert sim._marker_consumed is True
    train = trains.get(0)
    assert train.current_node_id != ""


def test_simulator_start_with_auto_plan_stays_parked():
    network, _ = _network_from_track(TEST_TRACK)
    node_ids = network.marker_node_ids()
    plan = _simulator_plan(
        [{"target_node_id": node_ids[0], "wait": {"type": "seconds", "seconds": 0}}],
        current_order_index=0,
    )
    project = Project("auto-sim", {"rails": [], "settings": {}, "trains": [plan]})
    trains = _make_trains(network, _planner_for(network))
    trains.set_project(project)
    sim = Simulator(network, trains)
    sim.start()

    train = trains.get(0)
    assert train.control_mode == ControlMode.Automatic
    assert train.halted_by_stop
    assert train.executor.status == ExecutorState.PAUSED
    assert sim._sim_device.speed == 0
    assert sim._run_task is None
    assert train.current_node_id != ""
