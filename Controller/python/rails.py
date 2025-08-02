from __future__ import annotations

from enum import IntEnum
from PySide6.QtCore import QAbstractListModel, Slot, Property, Signal
from PySide6.QtCore import QEnum, Qt, QModelIndex, QByteArray

from rail import Rail
from rail import RailType

class Rails(QAbstractListModel):

    @QEnum
    class Role(IntEnum):
        ObjectRole = Qt.ItemDataRole.UserRole

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._railways = []

    def rowCount(self, parent=QModelIndex()):
        return len(self._railways)

    def data(self, index: QModelIndex, role: int):
        row = index.row()
        if row < self.rowCount():
            if role == Rails.Role.ObjectRole:
                return self._railways[row]
        return None

    def roleNames(self):
        roles = super().roleNames()
        roles[Rails.Role.ObjectRole] = QByteArray(b"object")
        return roles

    @Slot(int)
    def createRail(self, type):
        print("wanna create", type)

    def append(self, rail):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._railways.append(rail)
        rail.disconnected.connect(self.rail_disconnected)
        self.endInsertRows()
        print("appended")

    def remove(self, rail):
        index = self._railways.index(rail)
        if index > -1:
            self.beginRemoveRows(QModelIndex(), index, index)
            self._railways.remove(rail)
            self.endRemoveRows()

