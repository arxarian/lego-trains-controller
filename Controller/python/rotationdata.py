from __future__ import annotations

from PySide6.QtCore import QObject, Slot, Property, Signal, QPoint
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "TrainView"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class RotationData(QObject):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._dir = 0
        self._angle = 0
        self._point = QPoint(0, 0)
        self._visible = True
        self._next = 0

    def angle(self):
        return self._angle

    def set_angle(self, value):
        self._angle = value
        self.angle_changed.emit()

    angle_changed = Signal()
    angle = Property(float, angle, set_angle, notify=angle_changed)

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

    def visible(self):
        return self._visible

    def set_visible(self, value):
        self._visible = value
        self.visible_changed.emit()

    visible_changed = Signal()
    visible = Property(bool, visible, set_visible, notify=visible_changed)

    def next(self):
        return self._next

    def set_next(self, value):
        self._next = value
        self.next_changed.emit()

    next_changed = Signal()
    next = Property(int, next, set_next, notify=next_changed)
