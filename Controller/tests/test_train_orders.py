from unittest.mock import MagicMock

import pytest
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication

from python.items.train_device_sim import TrainDeviceSim
from python.items.train import Train, ControlMode
from python.models.trains import Trains


@pytest.fixture(scope="session", autouse=True)
def ensure_qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def _make_train():
    network = MagicMock()
    network.find_node_by_color.return_value = None
    device = TrainDeviceSim(name="sim")
    return Train(device, network), network, device


def test_add_remove_clear_orders():
    train, _, _ = _make_train()

    assert train.orders.count == 0
    assert train.current_order_index == 0
    assert train.control_mode == ControlMode.Manual

    train.add_order("1A10", 0.0)
    train.add_order("2B20", 5.0)
    train.add_order("3C30", 1.5)

    assert train.orders.count == 3
    assert train.orders.get(0).target_node_id == "1A10"
    assert train.orders.get(1).target_node_id == "2B20"
    assert train.orders.get(1).wait_seconds == 5.0
    assert train.orders.get(2).target_node_id == "3C30"

    train.remove_order(1)
    assert train.orders.count == 2
    assert train.orders.get(0).target_node_id == "1A10"
    assert train.orders.get(1).target_node_id == "3C30"

    train.clear_orders()
    assert train.orders.count == 0
    assert train.current_order_index == 0


def test_set_wait_and_move_order():
    train, _, _ = _make_train()
    train.add_order("a", 0.0)
    train.add_order("b", 0.0)
    train.add_order("c", 0.0)

    train.set_wait(1, 7.5)
    assert train.orders.get(1).wait_seconds == 7.5

    train.set_current_order_index(1)
    train.move_order(0, 2)
    assert [train.orders.get(i).target_node_id for i in range(3)] == ["b", "c", "a"]
    assert train.current_order_index == 0


def test_remove_order_adjusts_current_index():
    train, _, _ = _make_train()
    train.add_order("a", 0.0)
    train.add_order("b", 0.0)
    train.add_order("c", 0.0)
    train.set_current_order_index(2)

    train.remove_order(0)
    assert train.current_order_index == 1
    assert train.orders.get(1).target_node_id == "c"

    train.remove_order(1)
    assert train.current_order_index == 0
    assert train.orders.count == 1


def test_localization_unchanged_with_orders():
    train, network, device = _make_train()
    train.add_order("1A10", 0.0)

    device.set_color(QColor("#ff0000"))
    network.find_node_by_color.assert_called()
    assert train.orders.count == 1
    assert train.current_node_id == ""


def _make_trains(network=None):
    if network is None:
        network = MagicMock()
        network.has_graph = True
        network.node_id_for_marker.return_value = "13A0"
    devices = MagicMock()
    return Trains(network, devices), network


def test_add_order_for_marker():
    trains, network = _make_trains()
    trains.add_train(TrainDeviceSim(name="sim"))

    assert trains.add_order_for_marker(0, 13, "A", 0) is True
    network.node_id_for_marker.assert_called_with(13, "A", 0)
    train = trains.get(0)
    assert train.orders.count == 1
    assert train.orders.get(0).target_node_id == "13A0"
    assert train.orders.get(0).wait_seconds == 0.0
    assert trains.last_order_hint == "Added order 13A0"


def test_add_order_for_marker_no_train():
    trains, _ = _make_trains()

    assert trains.add_order_for_marker(0, 13, "A", 0) is False
    assert trains.last_order_hint == "No planning-target train"


def test_add_order_for_marker_no_graph():
    network = MagicMock()
    network.has_graph = False
    network.node_id_for_marker.return_value = ""
    trains, _ = _make_trains(network)
    trains.add_train(TrainDeviceSim(name="sim"))

    assert trains.add_order_for_marker(0, 13, "A", 0) is False
    assert trains.get(0).orders.count == 0
    assert trains.last_order_hint == "No graph"


def test_add_order_for_marker_unknown_node():
    network = MagicMock()
    network.has_graph = True
    network.node_id_for_marker.return_value = ""
    trains, _ = _make_trains(network)
    trains.add_train(TrainDeviceSim(name="sim"))

    assert trains.add_order_for_marker(0, 13, "A", 0) is False
    assert trains.get(0).orders.count == 0
    assert trains.last_order_hint == "Marker is not a graph node"
