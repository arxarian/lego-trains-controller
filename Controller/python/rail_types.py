# This Python file uses the following encoding: utf-8

from __future__ import annotations

import json

from enum import IntEnum
from PySide6.QtCore import QAbstractListModel, Slot, QEnum, Qt, QModelIndex, QByteArray, Signal, Property

from rail_type import RailType

class RailTypes(QAbstractListModel):

    @QEnum
    class Role(IntEnum):
        ObjectRole = Qt.ItemDataRole.UserRole

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._railsActive = True
        self._items = []

        self.load_data()

    @Slot(QModelIndex, result=int)
    def rowCount(self, parent=QModelIndex()):
        return len(self._items)

    def data(self, index: QModelIndex, role: int):
        row = index.row()
        if row < self.rowCount():
            if role == RailTypes.Role.ObjectRole:
                return self._items[row]
        return None

    def roleNames(self):
        roles = super().roleNames()
        roles[RailTypes.Role.ObjectRole] = QByteArray(b"object")
        return roles

    def load_data(self):
        with open("resources/rail_types.json") as json_data:
            data = json.load(json_data)

            self.beginInsertRows(QModelIndex(), 0, len(data))
            self._items = [RailType(data=d, parent=self) for d in data]
            self.endInsertRows()

    def railsActive(self):
        return self._railsActive

    def set_railsActive(self, value):
        self._railsActive = value
        self.railsActive_changed.emit()

    railsActive_changed = Signal()
    railsActive = Property(bool, railsActive, set_railsActive, notify=railsActive_changed)
