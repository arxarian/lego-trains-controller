from __future__ import annotations

from enum import IntEnum
from PySide6.QtCore import QAbstractListModel, Slot, QEnum, Qt, QModelIndex, QByteArray

from marker import Marker

class Markers(QAbstractListModel):

    @QEnum
    class Role(IntEnum):
        ObjectRole = Qt.ItemDataRole.UserRole

    def __init__(self, data: list=None, parent=None) -> None:
        super().__init__(parent)
        data = data or []
        self._items = [Marker.load_data(d, self) for d in data]

    @Slot(QModelIndex, result=int)
    def rowCount(self, parent=QModelIndex()):
        return len(self._items)

    def data(self, index: QModelIndex, role: int):
        row = index.row()
        if row < self.rowCount():
            if role == Markers.Role.ObjectRole:
                return self._items[row]
        return None

    def roleNames(self):
        roles = super().roleNames()
        roles[Markers.Role.ObjectRole] = QByteArray(b"object")
        return roles

    def setModel(self, data):
        self.beginInsertRows(QModelIndex(), 0, len(data))
        for i in data:
            self._items.append(Marker(data=i, parent=self))
        self.endInsertRows()

    def save_data(self):
        data = [marker.save_data() for marker in self._items]
        return data

    def load_data(data, parent):
        return Markers(data=data, parent=parent)
