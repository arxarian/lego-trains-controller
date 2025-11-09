from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Property, Slot
from PySide6.QtQml import QmlElement
from PySide6.QtGui import QColor

from rotator import Rotator

QML_IMPORT_NAME = "TrainView"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class Marker(QObject):

    def __init__(self, data: dict=None, color=None, index=-1, parent=None):
        super().__init__(parent)
        self._visible = False if color is None else True
        self._index = index
        self._color = color
        self._rotator = None    # set in load_metadata
        self._distance = 0      # set in load_metadata

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
        if self._color is not None:
            return { "index": self._index, "color": self._color.name() }

    @Slot()
    def remove(self):
        self.set_color(None)
        self.set_visible(False)

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

    def index(self):
        return self._index

    def set_index(self, value):
        self._index = value
        self.index_changed.emit()

    index_changed = Signal()
    index = Property(int, index, set_index, notify=index_changed)

    def rotator(self):
        return self._rotator

    rotator = Property(QObject, rotator, constant=True)

    def distance(self):
        return self._distance

    def set_distance(self, value):
        self._distance = value
        self.distance_changed.emit()

    distance_changed = Signal()
    distance = Property(int, distance, set_distance, notify=distance_changed)
