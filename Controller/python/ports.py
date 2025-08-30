from __future__ import annotations

from enum import IntEnum
from PySide6.QtCore import QAbstractListModel, QObject, Slot
from PySide6.QtCore import QEnum, Qt, QModelIndex, QByteArray

from port import Port

class Ports(QAbstractListModel):

    @QEnum
    class Role(IntEnum):
        ObjectRole = Qt.ItemDataRole.UserRole

    def __init__(self, connectors, parent=None) -> None:
        super().__init__(parent)
        self._ports = []
        self._connectors = connectors

    @Slot(QModelIndex, result=int)
    def rowCount(self, parent=QModelIndex()):
        return len(self._ports)

    def data(self, index: QModelIndex, role: int):
        row = index.row()
        if row < self.rowCount():
            if role == Ports.Role.ObjectRole:
                return self._ports[row]
        return None

    def roleNames(self):
        roles = super().roleNames()
        roles[Ports.Role.ObjectRole] = QByteArray(b"object")
        return roles

    def setModel(self, data):
        self.beginInsertRows(QModelIndex(), 0, len(data))
        for i in data:
            self._ports.append(Port(i, self))
        self.endInsertRows()

    def portByIndex(self, index):
        for port in self._ports:
            if index in port.connectors:
                return port
            return None

    def connectTo(self, connectorIndex, toRailId):
        port = self.portByIndex(connectorIndex)
        if port:
            port.set_connectedRailId(toRailId)
            for index in port.connectors:
                # make connectors invisible
                self._connectors.get(index).set_visible(False)
