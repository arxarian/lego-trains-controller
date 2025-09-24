# This Python file uses the following encoding: utf-8

from __future__ import annotations

import json

from enum import IntEnum
from PySide6.QtCore import QAbstractListModel, Slot, QEnum, Qt, QModelIndex, QByteArray

from marker_type import MarkerType

class MarkerTypes(QAbstractListModel):

    @QEnum
    class Role(IntEnum):
        ObjectRole = Qt.ItemDataRole.UserRole

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._items = []

        self.load_data()

    @Slot(QModelIndex, result=int)
    def rowCount(self, parent=QModelIndex()):
        return len(self._items)

    def data(self, index: QModelIndex, role: int):
        row = index.row()
        if row < self.rowCount():
            if role == MarkerTypes.Role.ObjectRole:
                return self._items[row]
        return None

    def roleNames(self):
        roles = super().roleNames()
        roles[MarkerTypes.Role.ObjectRole] = QByteArray(b"object")
        return roles

    def load_data(self):
        with open("resources/marker_types.json") as json_data:
            data = json.load(json_data)

            self.beginInsertRows(QModelIndex(), 0, len(data))
            self._items = [MarkerType(data=d, parent=self) for d in data]
            self.endInsertRows()

