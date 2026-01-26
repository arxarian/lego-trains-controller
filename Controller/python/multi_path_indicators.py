# This Python file uses the following encoding: utf-8
from __future__ import annotations

from enum import IntEnum
from PySide6.QtCore import QAbstractListModel, QModelIndex, Slot, QByteArray, QEnum, Qt

from multi_path_indicator import MultiPathIndicator

class MultiPathIndicators(QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = []

    @QEnum
    class Role(IntEnum):
        ObjectRole = Qt.ItemDataRole.UserRole

    @Slot(QModelIndex, result=int)
    def rowCount(self, parent=QModelIndex()):
        return len(self._items)

    def data(self, index: QModelIndex, role: int):
        row = index.row()
        if row < self.rowCount():
            if role == MultiPathIndicators.Role.ObjectRole:
                return self._items[row]
        return None

    def roleNames(self):
        roles = super().roleNames()
        roles[MultiPathIndicators.Role.ObjectRole] = QByteArray(b"object")
        return roles

    def setModel(self, metaData):
        path_ids = set()
        for d in metaData:
            if "path_id" in d and d["path_id"] != None and d["path_id"] != "":
                path_ids.add(d["path_id"])
        if len(path_ids) == 0:
            path_ids.add("A")

        self.beginInsertRows(QModelIndex(), 0, len(path_ids))
        colors = ["gold", "red"]    # TODO - resolve how to use more colors in case of more paths
        for i, id in enumerate(path_ids):
            self._items.append(MultiPathIndicator(id=id, color=colors[i], parent=self))
        self.endInsertRows()
