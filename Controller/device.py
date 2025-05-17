from __future__ import annotations

import asyncio

from PySide6.QtCore import QObject, Slot, Property, Signal
from PySide6.QtGui import QColor

PYBRICKS_COMMAND_EVENT_CHAR_UUID = "c5f50002-8280-46da-89f4-6d8051e4aeef"
TRANSPARENT_COLOR = QColor(0, 0, 0, 0)

class Device(QObject):

    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.client = client
        self.ready_event = asyncio.Event()
        self._color = TRANSPARENT_COLOR

    def color(self):
        return self._color

    def set_color(self, value):
        self._color = value
        self.color_changed.emit()

    color_changed = Signal()
    color = Property(QColor, color, set_color, notify=color_changed)

    async def set_rx_method(self):
        def handle_rx(_, data: bytearray):
            if data[0] == 0x01:  # "write stdout" event (0x01)
                payload = data[1:4]

                if payload == b"rdy":
                    self.ready_event.set()
                elif payload == b"vol":
                    print("Voltage:", int.from_bytes(data[4:], 'big'))
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
