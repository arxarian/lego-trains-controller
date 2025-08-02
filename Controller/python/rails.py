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

    @Slot(int, result=Rail)
    def createRail(self, type) -> Rail:
        # append a new one
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._railways.append(Rail(type))
        self.endInsertRows()
        # return it
        return self._railways[-1]

    def remove(self, rail):
        index = self._railways.index(rail)
        if index > -1:
            self.beginRemoveRows(QModelIndex(), index, index)
            self._railways.remove(rail)
            self.endRemoveRows()

