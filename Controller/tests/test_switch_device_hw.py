import pytest
from PySide6.QtWidgets import QApplication

from python.items.rail import Rail, RailType
from python.items.switch_device_hw import SwitchDeviceHW
from python.models.switch_devices import SwitchDevices


@pytest.fixture(scope="session", autouse=True)
def ensure_qapp():
    app = QApplication.instance() or QApplication([])
    yield app


class _FakeBle:
    def __init__(self):
        self.sent = []
        self.client = object()

    def send(self, cmd, data=b"", response=True):
        self.sent.append((cmd, data, response))


def test_switch_device_hw_set_position_sends_pos_and_updates_rail():
    rail = Rail(type=RailType.SwitchLeft, id=1)
    devices = SwitchDevices()
    ble = _FakeBle()
    device = SwitchDeviceHW(client=ble.client, hub_name="sw", ble=ble)
    # Avoid starting async notify/voltage tasks asserting on real BLE in unit test:
    # constructor already scheduled tasks; they are harmless without a running loop wait.
    devices.append(device)
    devices.assignToRail(rail, device)

    device.set_position("B")

    assert ("pos", b"B", True) in ble.sent
    assert rail.switch_position == "B"
    assert device.position == "B"


def test_switch_device_hw_role_is_switch():
    ble = _FakeBle()
    device = SwitchDeviceHW(client=ble.client, hub_name="sw", ble=ble)
    assert device.role == "switch"
    assert device.isSimulated is False
