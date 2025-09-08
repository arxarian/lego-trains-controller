from __future__ import annotations

from PySide6.QtCore import QObject, Slot, Signal, Qt
from PySide6.QtQml import QmlElement
from rail import RailType
from dataclasses import dataclass

QML_IMPORT_NAME = "TrainView"
QML_IMPORT_MAJOR_VERSION = 1

@dataclass
class ConnectorEvent:
    railType: RailType
    railId: int
    connectorIndex: int

@QmlElement
class ConnectorRegister(QObject):
    newEvents = Signal()
    appendRail = Signal(ConnectorEvent)
    connectRails = Signal(ConnectorEvent, ConnectorEvent)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._events = []
        self.newEvents.connect(self.process, Qt.QueuedConnection);


    @Slot(int)
    @Slot(int, int, int)
    def addEvent(self, railType: RailType, railId: int=-1, connectorIndex: int=-1):
        self._events.append(ConnectorEvent(railType, railId, connectorIndex))
        self.newEvents.emit()

    def process(self):
        size = len(self._events)
        if size == 1:
            self.appendRail.emit(self._events.pop())

        elif size == 2:
            self.connectRails.emit(self._events.pop(), self._events.pop())

        elif size > 2:
            print("unexpected number of events", size, "clearing...")
            self._events.clear()

connectorRegister = ConnectorRegister()


