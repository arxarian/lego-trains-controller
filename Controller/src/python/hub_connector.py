# This Python file uses the following encoding: utf-8
from __future__ import annotations

import asyncio

from PySide6.QtCore import QObject, Slot, Property, Signal
from bleak import BleakScanner, BleakClient

from python.hub_role import resolve_hub_target
from python.items.ble_device import BleDevice
from python.items.train_device_hw import TrainDeviceHW
from python.items.switch_device_hw import SwitchDeviceHW

ROLE_WAIT_TIMEOUT_S = 15


class HubConnector(QObject):
    """Role-neutral BLE discover/connect. Routes hubs into TrainDevices or SwitchDevices."""

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

    async def _wait_for_role(self, ble: BleDevice) -> str | None:
        """Probe notifications until rol payload arrives or timeout."""
        role_future: asyncio.Future[str] = asyncio.get_running_loop().create_future()

        def handle_rx(_, data: bytearray):
            if not data or data[0] != 0x01:
                return
            payload = data[1:4]
            if payload == b"rdy":
                ble.ready_event.set()
            elif payload == b"rol":
                role = data[4:].decode("utf-8", errors="replace").strip().lower()
                if not role_future.done():
                    role_future.set_result(role)
            elif payload == b"int":
                # Wait for rol that follows int; ignore here.
                pass

        await ble.start_notify(handle_rx)
        try:
            return await asyncio.wait_for(role_future, timeout=ROLE_WAIT_TIMEOUT_S)
        except asyncio.TimeoutError:
            return None

    @Slot(str)
    def connect_to(self, hub_name):
        """Connect, wait for hub role handshake, route to train or switch model."""
        print("Wanna connect to", hub_name)

        async def async_connect_to():
            device = await BleakScanner.find_device_by_name(hub_name)

            if device is None:
                print(f"could not find hub with name: {hub_name}")
                return

            print("Found", hub_name)

            client = BleakClient(device)  # TODO add handle disconnect
            await client.connect()
            if not client.is_connected:
                print("Connection to", hub_name, "failed")
                return

            print("Connected — waiting for hub role (start the program on the hub)")
            ble = BleDevice(client)
            role = await self._wait_for_role(ble)
            target = resolve_hub_target(role)

            if target is None:
                print(
                    f"Hub role handshake failed for {hub_name!r} "
                    f"(got {role!r}); disconnecting"
                )
                try:
                    await client.disconnect()
                except Exception as exc:
                    print(f"Disconnect after role failure: {exc}")
                return

            if target == "train":
                print(f"Routing {hub_name} as train")
                hw = TrainDeviceHW(
                    client=client,
                    hub_name=hub_name,
                    parent=self._train_devices,
                    ble=ble,
                )
                # int already observed before rol during probe
                hw.set_initialized(True)
                self._train_devices.append(hw)
            else:
                print(f"Routing {hub_name} as switch")
                hw = SwitchDeviceHW(
                    client=client,
                    hub_name=hub_name,
                    parent=self._switch_devices,
                    ble=ble,
                )
                hw.set_initialized(True)
                self._switch_devices.append(hw)

        asyncio.create_task(async_connect_to())
