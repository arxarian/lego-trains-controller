import pytest
from PySide6.QtWidgets import QApplication

from python.items.rail import Rail, RailType
from python.items.switch_device_hw import SwitchDeviceHW
from python.items.switch_device_sim import SwitchDeviceSim
from python.models.switch_devices import SwitchDevices


@pytest.fixture(scope="session", autouse=True)
def ensure_qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def test_switch_device_sim_role():
    device = SwitchDeviceSim(name="sim")
    assert device.role == "switch"
    assert device.isSimulated is True
    assert device.initialized is True


def test_set_position_updates_rail():
    rail = Rail(type=RailType.SwitchLeft, id=1)
    devices = SwitchDevices()
    device = devices.addSimulated()
    devices.assignToRail(rail, device)

    device.set_position("B")

    assert rail.switch_position == "B"
    assert rail.path_indicators.path_id_active == "B"
    assert device.position == "B"
    assert device.is_confirmed("B")


def test_rail_toggle_syncs_device_position():
    rail = Rail(type=RailType.SwitchRight, id=2)
    devices = SwitchDevices()
    device = devices.addSimulated()
    devices.assignToRail(rail, device)

    rail.toggleSwitchPosition()

    assert rail.switch_position == "B"
    assert device.position == "B"


def test_unbind_and_reassign():
    rail_a = Rail(type=RailType.SwitchLeft, id=10)
    rail_b = Rail(type=RailType.SwitchLeft, id=11)
    devices = SwitchDevices()
    device = devices.addSimulated()

    devices.assignToRail(rail_a, device)
    assert devices.deviceNameForRail(rail_a) == device.name
    revision_after_assign = devices.bindingsRevision
    assert revision_after_assign > 0

    devices.unbindRail(rail_a)
    assert devices.deviceForRail(rail_a) is None
    assert device.bound_rail is None
    assert devices.bindingsRevision > revision_after_assign

    devices.assignToRail(rail_b, device)
    assert devices.deviceForRail(rail_b) is device


def test_switch_rails_helper_excludes_non_switches():
    switch = Rail(type=RailType.SwitchLeft, id=1)
    straight = Rail(type=RailType.Straight, id=2)

    class _Rails:
        def items(self):
            return [switch, straight]

    devices = SwitchDevices()
    devices.set_rails_model(_Rails())

    only_switches = devices.switchRails()
    assert switch in only_switches
    assert straight not in only_switches


def test_unconfirmed_hardware_skips_sim_and_lists_pending_hubs():
    sim_rail = Rail(type=RailType.SwitchLeft, id=1)
    hw_rail = Rail(type=RailType.SwitchRight, id=2)
    devices = SwitchDevices()
    sim = devices.addSimulated()
    devices.assignToRail(sim_rail, sim)

    class _FakeBle:
        def __init__(self):
            self.client = object()

        def send(self, cmd, data=b"", response=True):
            pass

    hw = SwitchDeviceHW(client=object(), hub_name="sw", ble=_FakeBle())
    devices.append(hw)
    devices.assignToRail(hw_rail, hw)
    hw.set_position("B")

    pending = devices.unconfirmed_hardware([(sim_rail, "B"), (hw_rail, "B")])
    assert pending == [(hw, "B")]

    hw._on_position_ack("B")
    assert devices.unconfirmed_hardware([(sim_rail, "B"), (hw_rail, "B")]) == []
