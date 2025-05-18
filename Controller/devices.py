from __future__ import annotations

from PySide6.QtCore import QObject, Slot, Property, Signal
from bleak import BleakScanner, BleakClient
from device import Device

import asyncio

class Devices(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.devices = []
        self._discovered = []

    def discovered(self):
        return self._discovered

    discovered_changed = Signal()
    discovered = Property(list, discovered, notify=discovered_changed)

    @Slot(result=QObject)
    def firstDevice(self):  # TODO - change to a real model
        return self.devices[-1]

    @Slot()
    def discover(self):
        print("Discovering...")
        self._discovered = []
        self.discovered_changed.emit()

        async def async_disover(self):
            devices = await BleakScanner.discover()
            self._discovered = [device.name for device in devices if device.name is not None]
            self.discovered_changed.emit()

        asyncio.create_task(async_disover(self))

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
                self.devices.append(Device(client))
            else:
                print("Connection to", hub_name, "failed")

            await self.devices[-1].configure()

        asyncio.create_task(async_connect_to())
