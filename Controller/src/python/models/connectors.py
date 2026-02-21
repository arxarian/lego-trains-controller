from __future__ import annotations

from PySide6.QtCore import QObject, Slot, QModelIndex

from python.items.connector import Connector, State
from python.models.object_based_model import ObjectBasedModel

class Connectors(ObjectBasedModel[Connector]):

    _item_class = Connector

    def __init__(self, data: list=None, parent=None) -> None:
        super().__init__(parent)
        data = data or []
        self._items = [Connector.load_data(d, self) for d in data]

    def setModel(self, metaData):
        if len(self._items) > 0:
            # just update the model
            for i, d in enumerate(metaData):
                self._items[i].load_metadata(d)
        else:
            # create a new model
            self.beginInsertRows(QModelIndex(), 0, len(metaData))
            for d in metaData:
                self._items.append(Connector(d, self))
            self.endInsertRows()

    def connectTo(self, toRailId, connectorIndex):
        self._items[connectorIndex].set_connectedRailId(toRailId)

    def disconnectFrom(self, fromRailId):
        for connector in self._items:
            if connector.connectedRailId == fromRailId:
                connector.set_connectedRailId(State.NotConnected)

    def save_data(self):
        data = [connector.save_data() for connector in self._items]
        return data

    def load_data(data, parent):
        return Connectors(data=data, parent=parent)

    @Slot(result=int)
    def activeCount(self):
        return sum(1 for item in self._items if item.connected())

    @Slot(int, result=QObject)
    def findFromConnector(self, siblingRailId):
        return next((c for c in self._items if c.connectedRailId == siblingRailId), None)

    @Slot(result=QObject)
    def setNextConnector(self):
        for connector in self._items:
            if connector.connected():
                nextConnector = self._items[connector.next]
                nextConnector.set_connectedRailId(connector.connectedRailId)
                connector.set_connectedRailId(State.NotConnected)
                return nextConnector
        return None

    @Slot(result=QObject)
    def getFirstConnected(self):
        for connector in self._items:
            if connector.connected():
                return connector
        return None

    @Slot(int, result=QObject)
    def getByName(self, name: str):
        for connector in self._items:
            if connector._name == name:
                return connector
        return None
