# This Python file uses the following encoding: utf-8
from __future__ import annotations

import asyncio

from PySide6.QtCore import Slot
from PySide6.QtGui import QColor
from PySide6.QtQml import QmlElement

from python.items.ble_device import BleDevice
from python.items.train_device import TrainDevice, TRANSPARENT_COLOR

QML_IMPORT_NAME = "TrainView"
QML_IMPORT_MAJOR_VERSION = 1

VOLTAGE_REFRESH_INTERVAL = 60

@QmlElement
class TrainDeviceHW(TrainDevice):
    """Real BLE train hub."""

    def __init__(self, client, hub_name="unknown", parent=None, *, ble=None):
        super().__init__(name=hub_name, initialized=False, minimal_speed=-100, parent=parent)

        self._ble = ble if ble is not None else BleDevice(client)
        asyncio.create_task(self._set_rx_method())
        asyncio.create_task(self._async_voltage_status())

    @property
    def client(self):
        return self._ble.client

    @property
    def ready_event(self):
        return self._ble.ready_event

    async def _async_voltage_status(self):
        await self._ble.ready_event.wait()
        self.send("vol")
        await asyncio.sleep(VOLTAGE_REFRESH_INTERVAL)
        asyncio.create_task(self._async_voltage_status())

    def _apply_speed(self, value):
        print("Speed:", value)
        if value < 0:
            self.send("rev", abs(value).to_bytes(2, "big"))
        else:
            self.send("fwd", abs(value).to_bytes(2, "big"))

    def set_voltage(self, value):
        print("Voltage:", value)
        super().set_voltage(value)

    async def _set_rx_method(self):
        def handle_rx(_, data: bytearray):
            if data[0] == 0x01:  # "write stdout" event (0x01)
                payload = data[1:4]

                if payload == b"rdy":
                    self._ble.ready_event.set()
                elif payload == b"vol":
                    self.set_voltage(int.from_bytes(data[4:], "big"))
                elif payload == b"clr":
                    color = data[4:].decode("utf-8")
                    print("Color:", color)
                    if color == "NONE":
                        self.set_color(TRANSPARENT_COLOR)
                    else:
                        self.set_color(QColor(color))
                elif payload == b"int":
                    self.set_initialized(True)
                elif payload == b"rol":
                    pass
                else:
                    print("Received:", payload)

        await self._ble.start_notify(handle_rx)

    @Slot()
    def disconnect(self):
        print("About to disconnect...")

        async def async_disconnect():
            self.send("bye")
            await self._ble.disconnect_client()
            self.disconnected.emit(self)

        asyncio.create_task(async_disconnect())

    @Slot()
    def shutDown(self):
        async def async_shutDown():
            self.send("sht", b"", False)
            self.disconnected.emit(self)

        asyncio.create_task(async_shutDown())

    @Slot(str)
    def send(self, cmd, data=b"", response=True):
        self._ble.send(cmd, data, response)
