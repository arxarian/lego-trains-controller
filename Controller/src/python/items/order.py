from __future__ import annotations

from PySide6.QtCore import QObject, Property, Signal
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "TrainView"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class Order(QObject):

    def __init__(self, target_node_id: str, wait_seconds: float = 0.0, parent=None):
        super().__init__(parent)
        self._target_node_id = target_node_id
        self._wait_seconds = float(wait_seconds)

    def target_node_id(self):
        return self._target_node_id

    def set_target_node_id(self, value):
        if self._target_node_id != value:
            self._target_node_id = value
            self.target_node_id_changed.emit()

    target_node_id_changed = Signal()
    target_node_id = Property(str, target_node_id, set_target_node_id, notify=target_node_id_changed)

    def wait_seconds(self):
        return self._wait_seconds

    def set_wait_seconds(self, value):
        value = float(value)
        if self._wait_seconds != value:
            self._wait_seconds = value
            self.wait_seconds_changed.emit()

    wait_seconds_changed = Signal()
    wait_seconds = Property(float, wait_seconds, set_wait_seconds, notify=wait_seconds_changed)
