from __future__ import annotations

import asyncio

from PySide6.QtCore import QObject, Slot, Property, Signal
from PySide6.QtGui import QColor
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "TrainsView"
QML_IMPORT_MAJOR_VERSION = 1

PYBRICKS_COMMAND_EVENT_CHAR_UUID = "c5f50002-8280-46da-89f4-6d8051e4aeef"
TRANSPARENT_COLOR = QColor(0, 0, 0, 0)
VOLTAGE_REFRESH_INTERVAL = 60

@QmlElement
class Device(QObject):

    disconnected = Signal(QObject)

    def __init__(self, client, hub_name="unknown", parent=None):
        super().__init__(parent)
        self.client = client
        self.ready_event = asyncio.Event()
        self._color = TRANSPARENT_COLOR
        self._name = hub_name
        self._voltage = 0
        asyncio.create_task(self.async_voltage_status())

    async def async_voltage_status(self):
        await self.ready_event.wait()
        self.send("vol")
        await asyncio.sleep(VOLTAGE_REFRESH_INTERVAL)
        asyncio.create_task(self.async_voltage_status())

    def color(self):
        return self._color

    def set_color(self, value):
        self._color = value
        self.color_changed.emit()

    color_changed = Signal()
    color = Property(QColor, color, set_color, notify=color_changed)

    def voltage(self):
        return self._voltage

    def set_voltage(self, value):
        print("Voltage:", value)
        self._voltage = value
        self.voltage_changed.emit()

    voltage_changed = Signal()
    voltage = Property(int, voltage, set_voltage, notify=voltage_changed)

    def name(self):
        return self._name

    def set_name(self, value):
        self._name = value
        self.name_changed.emit()

    name_changed = Signal()
    name = Property(str, name, set_name, notify=name_changed)

    async def set_rx_method(self):
        def handle_rx(_, data: bytearray):
            if data[0] == 0x01:  # "write stdout" event (0x01)
                payload = data[1:4]

                if payload == b"rdy":
                    self.ready_event.set()
                elif payload == b"vol":
                    self.set_voltage(int.from_bytes(data[4:], 'big'))
                elif payload == b"clr":
                    color = data[4:].decode("utf-8")
                    if color == "NONE":
                        self.set_color(TRANSPARENT_COLOR)
                    else:
                        self.set_color(QColor(color))
                else:
                    print("Received:", payload)

        await self.client.start_notify(PYBRICKS_COMMAND_EVENT_CHAR_UUID, handle_rx)

    async def configure(self):
        await self.set_rx_method()
        print("Start the program on the hub now with the button.")

    @Slot()
    def disconnect(self):
        print("About to disconnect...")
        async def async_disconnect():
            self.send("bye")
            await self.client.disconnect()
            self.disconnected.emit(self)

        asyncio.create_task(async_disconnect())

    @Slot(str)
    def send(self, data):
        async def async_send(data):
            await self.ready_event.wait()
            self.ready_event.clear()

            # Send the data to the hub.
            await self.client.write_gatt_char(
                PYBRICKS_COMMAND_EVENT_CHAR_UUID,
                b"\x06" + data.encode(),  # prepend "write stdin" command (0x06)
                response=True
            )

        asyncio.create_task(async_send(data))
