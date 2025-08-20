from __future__ import annotations

from enum import IntEnum
from PySide6.QtCore import QAbstractListModel, QObject, Property, Signal, Slot
from PySide6.QtCore import QEnum, Qt, QModelIndex, QByteArray

from connector import Connector

class Connectors(QAbstractListModel):

    @QEnum
    class Role(IntEnum):
        ObjectRole = Qt.ItemDataRole.UserRole

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._connectors = []

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
        self.beginInsertRows(QModelIndex(), 0, len(data))
        for i in data:
            self._connectors.append(Connector(i))
        self.endInsertRows()

    @Slot(int, result=QObject)
    def get(self, index):
        if 0 <= index < len(self._connectors):
            return self._connectors[index]
        return None
