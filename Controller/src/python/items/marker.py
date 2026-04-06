from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Property, Slot, QPointF
from PySide6.QtQml import QmlElement
from PySide6.QtGui import QColor

from python.items.rotator import Rotator

QML_IMPORT_NAME = "TrainView"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class Marker(QObject):

    def __init__(self, data: dict=None, color=None, index=-1, parent=None):
        super().__init__(parent)
        self._visible = False if color is None else True
        self._index = index
        self._color = color
        self._enabled = True
        self._rotator = None    # set in load_metadata
        self._distance = 0      # set in load_metadata
        self._path_id = None    # set in load_metadata
        self._position = QPointF()

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

    def position(self):
        return self._position

    def set_position(self, value):
        self._position = value
        self.position_changed.emit()

    position_changed = Signal()
    position = Property(QPointF, position, set_position, notify=position_changed)

    def visible(self):
        return self._visible

    def set_visible(self, value):
        self._visible = value
        self.visible_changed.emit()
        from python.models.markers import Markers
        parent = self.parent()
        if isinstance(parent, Markers):
            parent.updateEnabledStates()

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

    def path_id(self):
        return self._path_id

    def set_path_id(self, value):
        self._path_id = value
        self.path_id_changed.emit()

    path_id_changed = Signal()
    path_id = Property(str, path_id, set_path_id, notify=path_id_changed)

    def enabled(self):
        return self._enabled

    def set_enabled(self, value):
        if self._enabled != value:
            self._enabled = value
            self.enabled_changed.emit()

    enabled_changed = Signal()
    enabled = Property(bool, enabled, set_enabled, notify=enabled_changed)
