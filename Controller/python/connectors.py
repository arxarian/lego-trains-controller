from __future__ import annotations

from enum import IntEnum
from PySide6.QtCore import QAbstractListModel, QObject, Property, Signal, Slot
from PySide6.QtCore import QEnum, Qt, QModelIndex, QByteArray

from connector import Connector, State

class Connectors(QAbstractListModel):

    @QEnum
    class Role(IntEnum):
        ObjectRole = Qt.ItemDataRole.UserRole

    def __init__(self, data: list=None, parent=None) -> None:
        super().__init__(parent)
        data = data or []
        self._connectors = [Connector.load_data(d, self) for d in data]

    @Slot(QModelIndex, result=int)
    def rowCount(self, parent=QModelIndex()):
        return len(self._connectors)

    def data(self, index: QModelIndex, role: int):
        row = index.row()
        if row < self.rowCount():
            if role == Connectors.Role.ObjectRole:
                return self._connectors[row]
        return None

    def roleNames(self):
        roles = super().roleNames()
        roles[Connectors.Role.ObjectRole] = QByteArray(b"object")
        return roles

    def setModel(self, data):
        if len(self._connectors) > 0:
            # just update the model
            for i, d in enumerate(data):
                self._connectors[i].load_metadata(d)
        else:
            # create a new model
            self.beginInsertRows(QModelIndex(), 0, len(data))
            for i in data:
                self._connectors.append(Connector(i, self))
            self.endInsertRows()

    def connectTo(self, toRailId, connectorIndex):
        self._connectors[connectorIndex].set_connectedRailId(toRailId)

    def disconnectFrom(self, fromRailId):
        for connector in self._connectors:
            if connector.connectedRailId == fromRailId:
                connector.set_connectedRailId(State.NotConnected)

    def save_data(self):
        data = [connector.save_data() for connector in self._connectors]
        return data

    def load_data(data, parent):
        return Connectors(data=data, parent=parent)

    @Slot(result=int)
    def connections(self):
        count = 0
        for connector in self._connectors:
            if connector.connected():
                count += 1
        return count

    @Slot(int, result=QObject)
    def findFromConnector(self, siblingRailId):
        for connector in self._connectors:
            if connector.connectedRailId == siblingRailId:
                return connector
        return None

    @Slot(result=QObject)
    def getAndSetNextConnector(self):
        for connector in self._connectors:
            if connector.connected():
                nextConnector = self._connectors[connector.next]
                nextConnector.set_connectedRailId(connector.connectedRailId)
                connector.set_connectedRailId(State.NotConnected)
                return nextConnector
        return None

    @Slot(result=QObject)
    def getFirstConnected(self):
        for connector in self._connectors:
            if connector.connected():
                return connector
        return None

    @Slot(int, result=QObject)
    def get(self, index):
        if 0 <= index < len(self._connectors):
            return self._connectors[index]
        return None
