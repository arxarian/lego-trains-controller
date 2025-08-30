from __future__ import annotations

from enum import IntEnum
from PySide6.QtCore import QAbstractListModel, QObject, Slot
from PySide6.QtCore import QEnum, Qt, QModelIndex, QByteArray

from port import Port

class Ports(QAbstractListModel):

    @QEnum
    class Role(IntEnum):
        ObjectRole = Qt.ItemDataRole.UserRole

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._ports = []

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

    # def connectTo(self, fromRailId, fromIndex):
    #     return

    # @Slot(int, result=QObject)
    # def get(self, index):
    #     if 0 <= index < len(self._ports):
    #         return self._ports[index]
    #     return None
