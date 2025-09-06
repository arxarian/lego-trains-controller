from __future__ import annotations

import json
from enum import IntEnum
from PySide6.QtCore import QAbstractListModel, Slot, Signal, Property
from PySide6.QtCore import QEnum, Qt, QModelIndex, QByteArray
from PySide6.QtQuick import QQuickItem

from rail import Rail
from rail import RailType
from connectors import Connectors

class Rails(QAbstractListModel):

    @QEnum
    class Role(IntEnum):
        ObjectRole = Qt.ItemDataRole.UserRole

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._railways = []
        self._registeredRails = {}
        self._loaded = True

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

    def loaded(self):
        return self._loaded

    def set_loaded(self, value):
        self._loaded = value
        self.loaded_changed.emit()

    loaded_changed = Signal()
    loaded = Property(bool, loaded, set_loaded, notify=loaded_changed)

    @Slot()
    def save_data(self):
        data = [rail.save_data() for rail in self._railways]
        with open("rails.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("saved")

    @Slot()
    def load_data(self):
        self.set_loaded(False)
        self.resetModel()

        with open("rails.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        self.beginResetModel()
        self._railways = [Rail.load_data(d, self) for d in data]
        self.endResetModel()
        print("loaded, size", len(self._railways))

    @Slot(QQuickItem, int)
    def registerRail(self, item, id):
        if not isinstance(item, QQuickItem):
            print("Cannot register, not a QQuickItem")
            return
        self._registeredRails[id] = item
        return

    @Slot(int, result=QQuickItem)
    def findRailItem(self, id) -> QQuickItem:
        if id in self._registeredRails:
            return self._registeredRails[id]
        return None

    @Slot()
    def checkLoaded(self):
        if len(self._registeredRails) == self.rowCount():
            self.set_loaded(True)

    @Slot(int, result=Rail)
    def findRailData(self, id) -> Rail:
        for rail in self._railways:
            if rail.id == id:
                return rail
        return None

    @Slot(int)
    @Slot(int, int, int)
    def append(self, type, fromRailId=-1, fromIndex=0):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._railways.append(Rail(type))

        if fromRailId > 0:
            # connect the new rail to the previous one
            self._railways[-1].connectTo(fromRailId, 0)
            # and the previous one to the new one
            rail = self.findRailData(fromRailId)
            if rail:
                rail.connectTo(self._railways[-1].id, fromIndex)

        self.endInsertRows()

    @Slot(int, result=int)
    def siblingOf(self, railId):
        for rail in self._railways:
            for row in range(rail.connectors.rowCount()):
                index = rail.connectors.index(row, 0)
                connector = rail.connectors.data(index, Connectors.Role.ObjectRole)
                if connector.connectedRailId == railId:
                    return rail.id
        return -1

    def resetModel(self):
        if (self.rowCount() == 0):
            return

        self._registeredRails.clear()

        self.beginRemoveRows(QModelIndex(), 0, self.rowCount() - 1)
        for rail in self._railways:
            rail.deleteLater()
        self._railways.clear()
        self.endRemoveRows()

    @Slot(Rail)
    def remove(self, rail):
        index = self._railways.index(rail)
        if index > -1:
            self.beginRemoveRows(QModelIndex(), index, index)
            self._railways.remove(rail)
            self.endRemoveRows()

