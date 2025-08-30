from __future__ import annotations

from PySide6.QtCore import QObject, Property, Signal
from PySide6.QtQml import QmlElement
from rotator import Rotator

QML_IMPORT_NAME = "TrainView"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class Port(QObject):

    def __init__(self, data, parent=None):
        super().__init__(parent)
        self._port = str()
        self._connectors = []

        self._connectorIndex = -1   # not defined in json
        self._connectedRailId = -1  # not defined in json

        self.load_metadata(data)

    def load_metadata(self, data):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def port(self):
        return self._port

    def set_port(self, value):
        self._port = value
        self.port_changed.emit()

    port_changed = Signal()
    port = Property(str, port, set_port, notify=port_changed)

    def connectors(self):
        return self._connectors

    def set_connectors(self, value):
        self._connectors = value
        self.connectors_changed.emit()

    connectors_changed = Signal()
    connectors = Property(list, connectors, set_connectors, notify=connectors_changed)

    def connectedRailId(self):
        return self._connectedRailId

    def set_connectedRailId(self, value):
        self._connectedRailId = value
        self.connectedRailId_changed.emit()

    connectedRailId_changed = Signal()
    connectedRailId = Property(int, connectedRailId, set_connectedRailId, notify=connectedRailId_changed)

    def connectorIndex(self):
        return self._connectorIndex

    def set_connectorIndex(self, value):
        self._connectorIndex = value
        self.connectorIndex_changed.emit()

    connectorIndex_changed = Signal()
    connectorIndex = Property(int, connectorIndex, set_connectorIndex, notify=connectorIndex_changed)

    def connected(self):
        return self._connectedRailId > 0
