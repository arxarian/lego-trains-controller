# This Python file uses the following encoding: utf-8
from __future__ import annotations

from PySide6.QtCore import Property
from PySide6.QtQml import QmlElement

from python.items.switch_device import SwitchDevice

QML_IMPORT_NAME = "TrainView"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class SwitchDeviceSim(SwitchDevice):
    """Simulated switch hub with no BLE connection."""

    def __init__(self, name="Simulated Switch", parent=None):
        super().__init__(name=name, initialized=True, parent=parent)

    def is_simulated(self):
        return True

    isSimulated = Property(bool, is_simulated, constant=True)

    def _apply_position(self, value):
        rail = self._bound_rail
        if rail is None:
            return
        rail.set_switch_position(value)
