# This Python file uses the following encoding: utf-8
from __future__ import annotations

from PySide6.QtCore import QObject, Property, Signal, Slot
from PySide6.QtGui import QColor

TRANSPARENT_COLOR = QColor(0, 0, 0, 0)

class TrainDevice(QObject):
    disconnected = Signal(QObject)
    color_changed = Signal()
    initialized_changed = Signal()
    speed_changed = Signal()
    voltage_changed = Signal()
    name_changed = Signal()

    def __init__(self, name="unknown", *, initialized=False, minimal_speed=0, parent=None):
        super().__init__(parent)
        self._color = TRANSPARENT_COLOR
        self._name = name
        self._voltage = 0
        self._speed = 0
        self._minimal_speed = minimal_speed
        self._initialized = initialized

    def color(self):
        return self._color

    def set_color(self, value):
        if self._color == value:
            return
        self._color = value
        self.color_changed.emit()

    color = Property(QColor, color, set_color, notify=color_changed)

    def initialized(self):
        return self._initialized

    def set_initialized(self, value):
        if self._initialized == value:
            return
        self._initialized = value
        self.initialized_changed.emit()

    initialized = Property(bool, initialized, set_initialized, notify=initialized_changed)

    def speed(self):
        return self._speed

    def set_speed(self, value):
        if value == self._speed:
            return
        self._speed = value
        self._apply_speed(value)
        self.speed_changed.emit()

    def _apply_speed(self, value):
        """Subclass hook for side effects (e.g. BLE motor commands)."""
        pass

    speed = Property(int, speed, set_speed, notify=speed_changed)

    def voltage(self):
        return self._voltage

    def set_voltage(self, value):
        if self._voltage == value:
            return
        self._voltage = value
        self.voltage_changed.emit()

    voltage = Property(int, voltage, set_voltage, notify=voltage_changed)

    def minimalSpeed(self):
        return self._minimal_speed

    minimalSpeed = Property(int, minimalSpeed, constant=True)

    def name(self):
        return self._name

    def set_name(self, value):
        if self._name == value:
            return
        self._name = value
        self.name_changed.emit()

    name = Property(str, name, set_name, notify=name_changed)

    @Slot()
    def disconnect(self):
        self.disconnected.emit(self)

    @Slot()
    def shutDown(self):
        self.disconnected.emit(self)
