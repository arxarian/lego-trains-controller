from __future__ import annotations

from PySide6.QtCore import Slot, Property, Signal, QModelIndex, QObject

from python.models.object_based_model import ObjectBasedModel

from bleak import BleakScanner, BleakClient
from python.items.device import Device

import asyncio

class Devices(ObjectBasedModel[Device]):

    _item_class = Device

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._discovered = []

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
