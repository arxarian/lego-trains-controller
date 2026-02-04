from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Property
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "TrainView"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class MultiPathIndicator(QObject):

    def __init__(self, id: id, parent=None):
        super().__init__(parent)
        self._path_id = id

    def path_id(self):
        return self._path_id

    def set_path_id(self, value):
        self._path_id = value
        self.path_id_changed.emit()

    path_id_changed = Signal()
    path_id = Property(str, path_id, set_path_id, notify=path_id_changed)
