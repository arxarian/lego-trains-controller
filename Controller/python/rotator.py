from __future__ import annotations

from PySide6.QtCore import QObject, Property, Signal
from PySide6.QtQml import QmlElement

import inspect

QML_IMPORT_NAME = "TrainView"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class Rotator(QObject):

    def __init__(self, x=0, y=0, angle=0, parent=None):
        super().__init__(parent)
        self._x = x
        self._y = y
        self._angle = angle

    def x(self):
        return self._x

    def set_x(self, value):
        self._x = value
        self.x_changed.emit()

    x_changed = Signal()
    x = Property(float, x, set_x, notify=x_changed)

    def y(self):
        return self._y

    def set_y(self, value):
        self._y = value
        self.y_changed.emit()

    y_changed = Signal()
    y = Property(float, y, set_y, notify=y_changed)

    def angle(self):
        return self._angle

    def set_angle(self, value):
        self._angle = value
        self.angle_changed.emit()

    angle_changed = Signal()
    angle = Property(float, angle, set_angle, notify=angle_changed)

    def save_data(self):
        return {"x": self._x, "y": self._y, "angle": self._angle}

    def load_data(data, parent):
        return Rotator(x=data.get("x", 0), y=data.get("y", 0), angle=data.get("angle", 0), parent=parent)
