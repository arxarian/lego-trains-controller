from __future__ import annotations

from PySide6.QtCore import QObject, Slot, Signal
from PySide6.QtQml import QmlElement
from PySide6.QtGui import QMouseEvent
from rail import RailType
from dataclasses import dataclass

QML_IMPORT_NAME = "TrainView"
QML_IMPORT_MAJOR_VERSION = 1

@dataclass
class ConnectorEvent:
    railType: RailType
    mouse: QMouseEvent
    railId: int
    connectorIndex: int

@QmlElement
class ConnectorRegister(QObject):
    newEvents = Signal()
    appendRail = Signal(ConnectorEvent)
    connectRails = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._events = []
        self.newEvents.connect(self.process);


    @Slot(int)
    @Slot(int, QObject, int, int)
    def addEvent(self, railType: RailType, event: QMouseEvent=None, railId: int=-1, connectorIndex: int=-1):
        self._events.append(ConnectorEvent(railType, event, railId, connectorIndex))
        self.newEvents.emit()

    def process(self):
        print("process")

        if len(self._events) == 1:
            self.appendRail.emit(self._events.pop())

        elif len(self._events) == 2:
            self.connectRails.emit()

connectorRegister = ConnectorRegister()


