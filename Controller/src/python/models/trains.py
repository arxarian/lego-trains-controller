from __future__ import annotations

from PySide6.QtCore import QModelIndex

from python.models.object_based_model import ObjectBasedModel
from python.items.train import Train

class Trains(ObjectBasedModel[Train]):

    _item_class = Train

    def __init__(self, network, parent=None):
        super().__init__(parent)
        self._network = network

    def add_train(self, device):
        train = Train(device=device, network=self._network, parent=self)
        device.disconnected.connect(lambda d: self.remove_by_device(d))
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._items.append(train)
        self.endInsertRows()
        return train

    def remove_by_device(self, device):
        train = next((t for t in self._items if t.device == device), None)
        if train is None:
            return
        index = self._items.index(train)
        self.beginRemoveRows(QModelIndex(), index, index)
        self._items.remove(train)
        self.endRemoveRows()
