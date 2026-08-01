import pytest
from PySide6.QtWidgets import QApplication

from python.hub_role import resolve_hub_target, route_device_by_role
from python.items.train_device_sim import TrainDeviceSim
from python.items.switch_device_sim import SwitchDeviceSim
from python.models.train_devices import TrainDevices
from python.models.switch_devices import SwitchDevices


@pytest.fixture(scope="session", autouse=True)
def ensure_qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.mark.parametrize(
    "role,expected",
    [
        ("train", "train"),
        ("TRAIN", "train"),
        ("switch", "switch"),
        ("Switch", "switch"),
        ("unknown", None),
        ("", None),
        (None, None),
    ],
)
def test_resolve_hub_target(role, expected):
    assert resolve_hub_target(role) == expected


def test_route_sim_train_by_role():
    trains = TrainDevices()
    switches = SwitchDevices()
    device = TrainDeviceSim(name="sim-train")

    target = route_device_by_role(device.role, trains, switches, device)

    assert target == "train"
    assert device in trains.items()
    assert device not in switches.items()


def test_route_sim_switch_by_role():
    trains = TrainDevices()
    switches = SwitchDevices()
    device = SwitchDeviceSim(name="sim-switch")

    target = route_device_by_role(device.role, trains, switches, device)

    assert target == "switch"
    assert device in switches.items()
    assert device not in trains.items()


def test_route_unknown_role_does_not_append():
    trains = TrainDevices()
    switches = SwitchDevices()
    device = TrainDeviceSim(name="orphan")

    target = route_device_by_role("bogus", trains, switches, device)

    assert target is None
    assert trains.rowCount() == 0
    assert switches.rowCount() == 0
