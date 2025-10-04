from __future__ import annotations

from enum import IntEnum
from PySide6.QtCore import QAbstractListModel, QObject, Slot
from PySide6.QtCore import QEnum, Qt, QModelIndex, QByteArray

from connector import Connector, State

class Connectors(QAbstractListModel):

    @QEnum
    class Role(IntEnum):
        ObjectRole = Qt.ItemDataRole.UserRole

    def __init__(self, data: list=None, parent=None) -> None:
        super().__init__(parent)
        data = data or []
        self._items = [Connector.load_data(d, self) for d in data]

    @Slot(QModelIndex, result=int)
    def rowCount(self, parent=QModelIndex()):
        return len(self._items)

    def data(self, index: QModelIndex, role: int):
        row = index.row()
        if row < self.rowCount():
            if role == Connectors.Role.ObjectRole:
                return self._items[row]
        return None

    def roleNames(self):
        roles = super().roleNames()
        roles[Connectors.Role.ObjectRole] = QByteArray(b"object")
        return roles

    def setModel(self, metaData):
        if len(self._items) > 0:
            # just update the model
            for i, d in enumerate(metaData):
                self._items[i].load_metadata(d)
        else:
            # create a new model
            self.beginInsertRows(QModelIndex(), 0, len(metaData))
            for d in metaData:
                self._items.append(Connector(d, self))
            self.endInsertRows()

    def connectTo(self, toRailId, connectorIndex):
        self._items[connectorIndex].set_connectedRailId(toRailId)

    def disconnectFrom(self, fromRailId):
        for connector in self._items:
            if connector.connectedRailId == fromRailId:
                connector.set_connectedRailId(State.NotConnected)

    def save_data(self):
        data = [connector.save_data() for connector in self._items]
        return data

    def load_data(data, parent):
        return Connectors(data=data, parent=parent)

    @Slot(result=int)
    def connections(self):
        count = 0
        for connector in self._items:
            if connector.connected():
                count += 1
        return count

    @Slot(int, result=QObject)
    def findFromConnector(self, siblingRailId):
        for connector in self._items:
            if connector.connectedRailId == siblingRailId:
                return connector
        return None

    @Slot(result=QObject)
    def setNextConnector(self):
        for connector in self._items:
            if connector.connected():
                nextConnector = self._items[connector.next]
                nextConnector.set_connectedRailId(connector.connectedRailId)
                connector.set_connectedRailId(State.NotConnected)
                return nextConnector
        return None

    @Slot(result=QObject)
    def getFirstConnected(self):
        for connector in self._items:
            if connector.connected():
                return connector
        return None

    @Slot(int, result=QObject)
    def get(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None
