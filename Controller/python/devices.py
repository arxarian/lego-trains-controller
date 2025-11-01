from __future__ import annotations

from enum import IntEnum
from PySide6.QtCore import QAbstractListModel, Slot, Property, Signal
from PySide6.QtCore import QEnum, Qt, QModelIndex, QByteArray

from bleak import BleakScanner, BleakClient
from device import Device

import asyncio

class Devices(QAbstractListModel):

    @QEnum
    class DeviceRole(IntEnum):
        ObjectRole = Qt.ItemDataRole.UserRole

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._devices = []
        self._discovered = []

    def rowCount(self, parent=QModelIndex()):
        return len(self._devices)

    def data(self, index: QModelIndex, role: int):
        row = index.row()
        if row < self.rowCount():
            if role == Devices.DeviceRole.ObjectRole:
                return self._devices[row]
        return None

    def roleNames(self):
        roles = super().roleNames()
        roles[Devices.DeviceRole.ObjectRole] = QByteArray(b"object")
        return roles

    def append(self, device):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._devices.append(device)
        device.disconnected.connect(self.device_disconnected)
        self.endInsertRows()

    def remove(self, device):
        index = self._devices.index(device)
        if index > -1:
            self.beginRemoveRows(QModelIndex(), index, index)
            self._devices.remove(device)
            self.endRemoveRows()

    def device_disconnected(self, device):
        if device in self._devices:
            self.remove(device)
            print("Disconnected")
        else:
            print("Unable to remove the device")

    def discovered(self):
        return self._discovered

    openDiscoverPopup = Signal()

    def set_discovered(self, value):
        self._discovered = value
        self.discovered_changed.emit()

    @Slot()
    def discover(self):
        print("Discovering...")
        self.set_discovered([])
        self.openDiscoverPopup.emit()

        async def async_discover(self):
            devices = await BleakScanner.discover()

            # TODO - when no device found, the busy indicator is still visible
            self.set_discovered([device.name for device in devices if device.name is not None])

        asyncio.create_task(async_discover(self))

    discovered_changed = Signal()
    discovered = Property(list, discovered, set_discovered, notify=discovered_changed)

    @Slot(str)
    def connect_to(self, hub_name):
        print("Wanna connect to", hub_name)

        async def async_connect_to():
            device = await BleakScanner.find_device_by_name(hub_name)

            if device is None:
                print(f"could not find hub with name: {hub_name}")
                return

            print("Found", hub_name)

            client = BleakClient(device)    # TODO add handle disconnect
            await client.connect()
            if client.is_connected:
                print("Connected")
                self.append(Device(client=client, hub_name=hub_name, parent=self))
            else:
                print("Connection to", hub_name, "failed")

        asyncio.create_task(async_connect_to())
