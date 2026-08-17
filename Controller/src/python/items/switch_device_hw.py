# This Python file uses the following encoding: utf-8
from __future__ import annotations

import asyncio

from PySide6.QtCore import Slot
from PySide6.QtQml import QmlElement

from python.items.ble_device import BleDevice
from python.items.switch_device import SwitchDevice

QML_IMPORT_NAME = "TrainView"
QML_IMPORT_MAJOR_VERSION = 1

VOLTAGE_REFRESH_INTERVAL = 60


@QmlElement
class SwitchDeviceHW(SwitchDevice):
    """Real BLE switch hub: set_position over GATT."""

    def __init__(self, client, hub_name="Switch Hub", parent=None, *, ble=None):
        super().__init__(name=hub_name, initialized=False, parent=parent)
        self._ble = ble if ble is not None else BleDevice(client)
        self._voltage = 0
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            pass
        else:
            asyncio.create_task(self._set_rx_method())
            asyncio.create_task(self._async_voltage_status())

    @property
    def client(self):
        return self._ble.client

    def _apply_position(self, value):
        try:
            self._ble.send("pos", value.encode("utf-8"))
        except Exception as exc:
            print(f"SwitchDeviceHW {self._name}: BLE set_position failed: {exc}")
        rail = self._bound_rail
        if rail is not None:
            rail.set_switch_position(value)

    def _on_position_ack(self, ack: str):
        print(f"SwitchDeviceHW {self._name}: position ack {ack}")
        self._confirm_position(ack)

    async def _async_voltage_status(self):
        await self._ble.ready_event.wait()
        self.send("vol")
        await asyncio.sleep(VOLTAGE_REFRESH_INTERVAL)
        asyncio.create_task(self._async_voltage_status())

    async def _set_rx_method(self):
        def handle_rx(_, data: bytearray):
            if not data or data[0] != 0x01:
                return
            payload = data[1:4]

            if payload == b"rdy":
                self._ble.ready_event.set()
            elif payload == b"vol":
                self._voltage = int.from_bytes(data[4:], "big")
                print(f"SwitchDeviceHW {self._name}: voltage {self._voltage}")
            elif payload == b"pos":
                ack = data[4:5].decode("utf-8", errors="replace")
                self._on_position_ack(ack)
            elif payload == b"int":
                self.set_initialized(True)
            elif payload == b"rol":
                # Role already consumed by HubConnector; ignore late duplicates.
                pass
            else:
                print("SwitchDeviceHW received:", payload)

        await self._ble.start_notify(handle_rx)

    @Slot()
    def disconnect(self):
        print("About to disconnect switch hub...")

        async def async_disconnect():
            try:
                self.send("bye")
                await self._ble.disconnect_client()
            except Exception as exc:
                print(f"SwitchDeviceHW disconnect error: {exc}")
            self.disconnected.emit(self)

        asyncio.create_task(async_disconnect())

    @Slot()
    def shutDown(self):
        async def async_shutDown():
            try:
                self.send("sht", b"", False)
            except Exception as exc:
                print(f"SwitchDeviceHW shutDown error: {exc}")
            self.disconnected.emit(self)

        asyncio.create_task(async_shutDown())

    @Slot(str)
    def send(self, cmd, data=b"", response=True):
        self._ble.send(cmd, data, response)
