from __future__ import annotations

from enum import IntEnum
from PySide6.QtCore import QAbstractListModel, Slot, Property, Signal
from PySide6.QtCore import QEnum, Qt, QModelIndex, QByteArray

from rail import Rail

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

    def append(self, device):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._railways.append(device)
        device.disconnected.connect(self.device_disconnected)
        self.endInsertRows()

    def remove(self, device):
        index = self._devices.index(device)
        if index > -1:
            self.beginRemoveRows(QModelIndex(), index, index)
            self._railways.remove(device)
            self.endRemoveRows()

