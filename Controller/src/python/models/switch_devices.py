# This Python file uses the following encoding: utf-8
from __future__ import annotations

from PySide6.QtCore import Slot, Signal, Property, QModelIndex, QObject

from python.models.object_based_model import ObjectBasedModel
from python.items.switch_device import SwitchDevice
from python.items.switch_device_sim import SwitchDeviceSim
from python.items.rail import Rail


class SwitchDevices(ObjectBasedModel[SwitchDevice]):
    """Switch actuators + rail bindings. Session-only bindings; TODO persist in project JSON."""

    _item_class = SwitchDevice

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._rails = None
        self._rail_to_device: dict[int, SwitchDevice] = {}
        self._sim_counter = 0
        self._bindings_revision = 0

    bindings_changed = Signal()
    bindings_revision_changed = Signal()

    def bindings_revision(self):
        return self._bindings_revision

    bindingsRevision = Property(
        int, bindings_revision, notify=bindings_revision_changed
    )

    def _notify_bindings_changed(self):
        self._bindings_revision += 1
        self.bindings_revision_changed.emit()
        self.bindings_changed.emit()

    def set_rails_model(self, rails):
        self.clear_bindings()
        self._rails = rails

    def clear_bindings(self):
        for device in list(self._items):
            self._disconnect_rail_signals(device)
            device.set_bound_rail(None)
        self._rail_to_device.clear()
        self._notify_bindings_changed()

    def clear_all(self):
        """Clear bindings and remove all devices (e.g. project change)."""
        self.clear_bindings()
        self.clear()

    def _disconnect_rail_signals(self, device: SwitchDevice):
        rail = device.bound_rail
        if rail is None:
            return
        try:
            rail.switch_position_changed.disconnect(self._on_rail_position_changed)
        except (RuntimeError, TypeError):
            pass

    def _on_rail_position_changed(self):
        rail = self.sender()
        if rail is None:
            return
        device = self._rail_to_device.get(rail.id)
        if device is None:
            return
        device.set_position(rail.switch_position)

    def append(self, device: SwitchDevice):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._items.append(device)
        device.disconnected.connect(self._device_disconnected)
        self.endInsertRows()

    def _device_disconnected(self, device):
        if device in self._items:
            self.unbind_device(device)
            self.remove(device)

    def unbind_device(self, device: SwitchDevice):
        rail = device.bound_rail
        if rail is None:
            return
        self._disconnect_rail_signals(device)
        self._rail_to_device.pop(rail.id, None)
        device.set_bound_rail(None)
        self._notify_bindings_changed()

    @Slot(result=QObject)
    def addSimulated(self):
        self._sim_counter += 1
        name = f"Simulated Switch {self._sim_counter}"
        device = SwitchDeviceSim(name=name, parent=self)
        self.append(device)
        return device

    @Slot(QObject, QObject)
    def assignToRail(self, rail, device):
        if rail is None or device is None:
            return
        if not isinstance(rail, Rail) or not rail.is_switch():
            return
        if not isinstance(device, SwitchDevice):
            return
        if rail.id in self._rail_to_device:
            self.unbindRail(rail)
        if device.bound_rail is not None:
            self.unbind_device(device)

        device.set_bound_rail(rail)
        self._rail_to_device[rail.id] = device
        rail.switch_position_changed.connect(self._on_rail_position_changed)
        device.set_position(rail.switch_position)
        self._notify_bindings_changed()

    @Slot(QObject)
    def unbindRail(self, rail):
        if rail is None:
            return
        device = self._rail_to_device.get(rail.id)
        if device is None:
            return
        self.unbind_device(device)

    @Slot(QObject, result=QObject)
    def deviceForRail(self, rail):
        if rail is None:
            return None
        return self._rail_to_device.get(rail.id)

    @Slot(QObject, result=str)
    def deviceNameForRail(self, rail):
        device = self.deviceForRail(rail)
        if device is None:
            return "No hub"
        return device.name

    @Slot(result=list)
    def unboundDevices(self):
        return [d for d in self._items if d.bound_rail is None]

    @Slot(result=list)
    def switchRails(self):
        if self._rails is None:
            return []
        return [r for r in self._rails.items() if r.is_switch()]

    def unconfirmed_hardware(self, required: list[tuple[Rail, str]]) -> list[tuple[SwitchDevice, str]]:
        """Bound hardware devices that still need a pos ack for the required path."""
        pending = []
        for rail, path_id in required or []:
            device = self._rail_to_device.get(getattr(rail, "id", None))
            if device is None or device.is_simulated():
                continue
            if device.is_confirmed(path_id):
                continue
            pending.append((device, path_id))
        return pending

    def command_required(self, required: list[tuple[Rail, str]]) -> None:
        """Send set_position to each bound device for the reserved switch path."""
        for rail, path_id in required or []:
            device = self._rail_to_device.get(getattr(rail, "id", None))
            if device is None:
                continue
            device.set_position(path_id)
