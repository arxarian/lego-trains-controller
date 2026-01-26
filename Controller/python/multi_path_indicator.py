from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Property
from PySide6.QtQml import QmlElement
from PySide6.QtGui import QColor


QML_IMPORT_NAME = "TrainView"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class MultiPathIndicator(QObject):

    def __init__(self, id: id, color, parent=None):
        super().__init__(parent)
        self._path_id = id
        self._active = False
        self._color = color

    def active(self):
        return self._active

    def set_active(self, value):
        self._active = value
        self.active_changed.emit()

    active_changed = Signal()
    active = Property(bool, active, set_active, notify=active_changed)

    def color(self):
        return self._color

    def set_color(self, value):
        self._color = value
        self.color_changed.emit()

    color_changed = Signal()
    color = Property(QColor, color, set_color, notify=color_changed)

    def path_id(self):
        return self._path_id

    def set_path_id(self, value):
        self._path_id = value
        self.path_id_changed.emit()

    path_id_changed = Signal()
    path_id = Property(str, path_id, set_path_id, notify=path_id_changed)
