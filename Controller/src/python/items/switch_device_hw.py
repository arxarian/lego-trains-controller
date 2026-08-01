# This Python file uses the following encoding: utf-8
from __future__ import annotations

from PySide6.QtQml import QmlElement

from python.items.switch_device import SwitchDevice

QML_IMPORT_NAME = "TrainView"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class SwitchDeviceHW(SwitchDevice):
    """Real BLE switch hub (SW1 stub: logical rail only; SW2 adds GATT)."""

    def __init__(self, name="Switch Hub", *, client=None, parent=None):
        # SW1: allow stub without client; SW2/F3 will require live BLE + role handshake.
        super().__init__(name=name, initialized=True, parent=parent)
        self._client = client

    def _apply_position(self, value):
        # TODO(SW2): send set_position over BleDevice
        print(f"SwitchDeviceHW {self._name}: set_position {value} (BLE stub)")
        rail = self._bound_rail
        if rail is None:
            return
        rail.set_switch_position(value)
