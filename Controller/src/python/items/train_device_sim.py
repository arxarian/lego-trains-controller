# This Python file uses the following encoding: utf-8
from __future__ import annotations

from PySide6.QtQml import QmlElement

from python.items.train_device import TrainDevice

QML_IMPORT_NAME = "TrainView"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class TrainDeviceSim(TrainDevice):
    """Simulated train hub with no BLE connection."""

    def __init__(self, name="Simulator", parent=None):
        super().__init__(name=name, initialized=True, minimal_speed=0, parent=parent)
