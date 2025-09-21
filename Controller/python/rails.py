from __future__ import annotations

import json
from enum import IntEnum
from PySide6.QtCore import QAbstractListModel, Slot, Signal, Property
from PySide6.QtCore import QEnum, Qt, QModelIndex, QByteArray
from PySide6.QtQuick import QQuickItem

from rail import Rail
from connectors import Connectors
from connectorregister import ConnectorEvent, ConnectorRegister

class Rails(QAbstractListModel):

    @QEnum
    class Role(IntEnum):
        ObjectRole = Qt.ItemDataRole.UserRole

    def __init__(self, connectorRegister: ConnectorRegister, parent=None) -> None:
        super().__init__(parent)
        self._rails = []
        self._registeredRails = {}      # id -> item
        self._loading = False
        connectorRegister.appendRail.connect(self.append)
        connectorRegister.connectRails.connect(self.connectRails)

    def rowCount(self, parent=QModelIndex()):
        return len(self._rails)

    def data(self, index: QModelIndex, role: int):
        row = index.row()
        if row < self.rowCount():
            if role == Rails.Role.ObjectRole:
                return self._rails[row]
        return None

    def roleNames(self):
        roles = super().roleNames()
        roles[Rails.Role.ObjectRole] = QByteArray(b"object")
        return roles

    def loading(self):
        return self._loading

    def set_loading(self, value):
        self._loading = value
        self.loading_changed.emit()

    loading_changed = Signal()
    loading = Property(bool, loading, set_loading, notify=loading_changed)

    def save_data(self) -> list:
        return [rail.save_data() for rail in self._rails]

    def load_data(self, data: list):
        self.set_loading(True)
        self.resetModel()

        self.beginResetModel()
        self._rails = data
        self.endResetModel()
        print("loaded, size", len(self._rails))

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
            self.set_loading(False)

    @Slot(int, result=Rail)
    def findRailData(self, id) -> Rail:
        for rail in self._rails:
            if rail.id == id:
                return rail

        print("rail", id, "not found")
        return None

    def connectRails(self, connector_0: ConnectorEvent, connector_1: ConnectorEvent):
            rail_0 = self.findRailData(connector_0.railId)
            rail_1 = self.findRailData(connector_1.railId)

            if rail_0 and rail_1:
                rail_0.connectTo(connector_1.railId, connector_0.connectorIndex)
                rail_1.connectTo(connector_0.railId, connector_1.connectorIndex)

    def append(self, fromEvent: ConnectorEvent):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._rails.append(Rail(type=fromEvent.railType, parent=self)) # the first rail has to be appended anyway

        if fromEvent.railId > 0:
            toRail = self._rails[-1]
            fromRail = self.findRailData(fromEvent.railId)

            # connect the new rail to the previous one
            toRail.connectTo(fromEvent.railId, 0)
            # and the previous one to the new one
            fromRail.connectTo(toRail.id, fromEvent.connectorIndex)

            toDir = toRail.connectors.get(0).dir
            fromDir = fromRail.connectors.get(fromEvent.connectorIndex).dir

            # if the dir is the same, set the next connector so for example when placing curved track,
            # the rotation is preserved
            if fromDir == toDir:
                toRail.connectors.setNextConnector()

        self.endInsertRows()

    @Slot(int, result=list)
    def findsiblingsOf(self, railId):
        siblings = []
        for rail in self._rails:
            for row in range(rail.connectors.rowCount()):
                index = rail.connectors.index(row, 0)
                connector = rail.connectors.data(index, Connectors.Role.ObjectRole)
                if connector.connectedRailId == railId:
                    siblings.append(rail.id)
        return siblings

    def resetModel(self):
        if (self.rowCount() == 0):
            return

        self._registeredRails.clear()

        self.beginRemoveRows(QModelIndex(), 0, self.rowCount() - 1)
        for rail in self._rails:
            rail.deleteLater()
        self._rails.clear()
        self.endRemoveRows()

    @Slot(Rail)
    def remove(self, rail):
        index = self._rails.index(rail)
        if index > -1:
            siblingsIds = self.findsiblingsOf(rail.id) # find siblings
            for id in siblingsIds:
                siblingRail = self.findRailData(id)
                if siblingRail: # set not connected for all connectors of siblings
                    siblingRail.disconnectFrom(rail.id)

            self.beginRemoveRows(QModelIndex(), index, index)
            self._rails.remove(rail)
            self.endRemoveRows()

