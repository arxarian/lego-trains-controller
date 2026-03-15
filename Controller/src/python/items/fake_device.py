from __future__ import annotations

from PySide6.QtCore import QObject, Property, Signal, Slot
from PySide6.QtGui import QColor

TRANSPARENT_COLOR = QColor(0, 0, 0, 0)


class FakeDevice(QObject):
    """Simulated device that mimics the Device interface without any BLE connection."""

    disconnected = Signal(QObject)

    def __init__(self, name="Simulator", parent=None):
        super().__init__(parent)
        self._color = TRANSPARENT_COLOR
        self._name = name
        self._speed = 0
        self._voltage = 0
        self._initialized = True

    def color(self):
        return self._color

    def set_color(self, value):
        self._color = value
        self.color_changed.emit()

    color_changed = Signal()
    color = Property(QColor, color, set_color, notify=color_changed)

    def name(self):
        return self._name

    name_changed = Signal()
    name = Property(str, name, notify=name_changed)

    def initialized(self):
        return self._initialized

    initialized_changed = Signal()
    initialized = Property(bool, initialized, notify=initialized_changed)

    def speed(self):
        return self._speed

    def set_speed(self, value):
        self._speed = value

    speed = Property(int, speed, set_speed)

    def voltage(self):
        return self._voltage

    voltage_changed = Signal()
    voltage = Property(int, voltage, notify=voltage_changed)

    @Slot()
    def disconnect(self):
        self.disconnected.emit(self)

    @Slot()
    def shutDown(self):
        self.disconnected.emit(self)
