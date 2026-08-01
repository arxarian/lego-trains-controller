# This Python file uses the following encoding: utf-8
from __future__ import annotations

from PySide6.QtCore import Slot, Signal, QModelIndex, QObject

from python.models.object_based_model import ObjectBasedModel
from python.items.train_device_hw import TrainDeviceHW


class TrainDevices(ObjectBasedModel[TrainDeviceHW]):
    """Connected real train hubs (discover/connect lives on HubConnector)."""

    _item_class = TrainDeviceHW

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

    device_connected = Signal(QObject)

    def append(self, device):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._items.append(device)
        device.disconnected.connect(self.device_disconnected)
        self.endInsertRows()
        self.device_connected.emit(device)

    def remove(self, device):
        index = self._items.index(device)
        if index > -1:
            self.beginRemoveRows(QModelIndex(), index, index)
            self._items.remove(device)
            self.endRemoveRows()

    def device_disconnected(self, device):
        if device in self._items:
            self.remove(device)
            print("Disconnected")
        else:
            print("Unable to remove the device")
