from __future__ import annotations

from PySide6.QtCore import QObject, Slot, Property, Signal, QPoint
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "TrainView"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class Connector(QObject):

    def __init__(self, data, parent=None):
        super().__init__(parent)
        self._name = str()
        self._dir = str()
        self._angle = 0
        self._point = QPoint(0, 0)
        self._next = 0
        self.rotation = 0
        self._visible = True       # not defined in json

        self.load_metadata_from_Json(data)

    def load_metadata_from_Json(self, data):
        for key, value in data.items():
            if hasattr(self, key):
                if key == "point":
                    self._point = QPoint(value["x"], value["y"])
                    continue
                setattr(self, key, value)

    def angle(self):
        return self._angle

    def set_angle(self, value):
        self._angle = value
        self.angle_changed.emit()

    angle_changed = Signal()
    angle = Property(float, angle, set_angle, notify=angle_changed)

    def name(self):
        return self._name

    def set_name(self, value):
        self._name = value
        self.name_changed.emit()

    name_changed = Signal()
    name = Property(str, name, set_name, notify=name_changed)

    def dir(self):
        return self._dir

    def set_dir(self, value):
        self._dir = value
        self.dir_changed.emit()

    dir_changed = Signal()
    dir = Property(str, dir, set_dir, notify=dir_changed)

    def point(self):
        return self._point

    def set_point(self, value):
        self._point = value
        self.point_changed.emit()

    point_changed = Signal()
    point = Property(QPoint, point, set_point, notify=point_changed)

    def next(self):
        return self._next

    def set_next(self, value):
        self._next = value
        self.next_changed.emit()

    next_changed = Signal()
    next = Property(int, next, set_next, notify=next_changed)

    def rotation(self):
        return self._rotation

    def set_rotation(self, value):
        self._rotation = value
        self.rotation_changed.emit()

    rotation_changed = Signal()
    rotation = Property(float, rotation, set_rotation, notify=rotation_changed)

    def visible(self):
        return self._visible

    def set_visible(self, value):
        self._visible = value
        self.visible_changed.emit()

    visible_changed = Signal()
    visible = Property(bool, visible, set_visible, notify=visible_changed)
