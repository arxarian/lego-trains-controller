from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Property
from PySide6.QtQml import QmlElement
from PySide6.QtGui import QColor

from rotator import Rotator

QML_IMPORT_NAME = "TrainView"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class Marker(QObject):

    def __init__(self, data: dict=None, color=None, parent=None):
        super().__init__(parent)
        self._visible = False
        self._color = color
        self._rotator = None

        self.load_metadata(data)

    def load_metadata(self, data):
        if data == None:
            return

        for key, value in data.items():
            if hasattr(self, key):
                if key == "rotator":
                    self._rotator = Rotator.load_data(value, self)
                    continue
                setattr(self, key, value)

    def save_data(self):
         return { "color": self._color.name() } if self._color is not None else {}

    def load_data(data, parent):
        return Marker(color=data.get("color", None), parent=parent)

    def visible(self):
        return self._visible

    def set_visible(self, value):
        self._visible = value
        self.visible_changed.emit()

    visible_changed = Signal()
    visible = Property(bool, visible, set_visible, notify=visible_changed)

    def color(self):
        return self._color

    def set_color(self, value):
        self._color = value
        self.color_changed.emit()

    color_changed = Signal()
    color = Property(QColor, color, set_color, notify=color_changed)

    def rotator(self):
        return self._rotator

    rotator = Property(QObject, rotator, constant=True)
