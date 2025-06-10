from __future__ import annotations

from PySide6.QtCore import QObject, Slot, Property, Signal, QPoint
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "TrainsView"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class RotationData(QObject):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._dir = 0
        self._angle = 0
        self._point = QPoint(0, 0)

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
    dir = Property(int, dir, set_dir, notify=dir_changed)

    def point(self):
        return self._point

    def set_point(self, value):
        self._point = value
        self.point_changed.emit()

    point_changed = Signal()
    point = Property(QPoint, point, set_point, notify=point_changed)

