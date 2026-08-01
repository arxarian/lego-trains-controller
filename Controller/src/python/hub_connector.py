# This Python file uses the following encoding: utf-8
from __future__ import annotations

import asyncio

from PySide6.QtCore import QObject, Slot, Property, Signal
from bleak import BleakScanner, BleakClient

from python.items.train_device_hw import TrainDeviceHW


class HubConnector(QObject):
    """Role-neutral BLE discover/connect. Routes hubs into TrainDevices or SwitchDevices.

    Until F3 (#164): after connect, hubs that complete the train init path are treated as trains.
    Switch role handshake is stubbed; use SwitchDevices.addSimulated() for switch assign UI.
    """

    openDiscoverPopup = Signal()
    discovered_changed = Signal()

    def __init__(self, train_devices, switch_devices, parent=None):
        super().__init__(parent)
        self._train_devices = train_devices
        self._switch_devices = switch_devices
        self._discovered = []

    def discovered(self):
        return self._discovered

    def set_discovered(self, value):
        self._discovered = value
        self.discovered_changed.emit()

    discovered = Property(list, discovered, set_discovered, notify=discovered_changed)

    @Slot()
    def discover(self):
        print("Discovering...")
        self.set_discovered([])
        self.openDiscoverPopup.emit()

        async def async_discover():
            devices = await BleakScanner.discover()
            # TODO - when no device found, the busy indicator is still visible
            self.set_discovered(
                [device.name for device in devices if device.name is not None]
            )

        asyncio.create_task(async_discover())

    @Slot(str)
    def connect_to(self, hub_name):
        """Connect and route by hub role. Pre-F3: always train after successful BLE connect."""
        print("Wanna connect to", hub_name)

        async def async_connect_to():
            device = await BleakScanner.find_device_by_name(hub_name)

            if device is None:
                print(f"could not find hub with name: {hub_name}")
                return

            print("Found", hub_name)

            client = BleakClient(device)  # TODO add handle disconnect
            await client.connect()
            if client.is_connected:
                print("Connected")
                # TODO(F3 #164): wait for role handshake; route train vs switch
                self._train_devices.append(
                    TrainDeviceHW(client=client, hub_name=hub_name, parent=self._train_devices)
                )
            else:
                print("Connection to", hub_name, "failed")

        asyncio.create_task(async_connect_to())
