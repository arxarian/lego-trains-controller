from __future__ import annotations

from PySide6.QtCore import QObject, Slot #Property, Signal

import asyncio
from bleak import BleakScanner, BleakClient

PYBRICKS_COMMAND_EVENT_CHAR_UUID = "c5f50002-8280-46da-89f4-6d8051e4aeef"

class Devices(QObject):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.client = None  # TODO - make an array
        self.ready_event = asyncio.Event()

    @Slot(str)
    def send(self, data):
        async def async_send(data):
            await self.ready_event.wait()
            self.ready_event.clear()

            # Send the data to the hub.
            await self.client.write_gatt_char(
                PYBRICKS_COMMAND_EVENT_CHAR_UUID,
                b"\x06" + b"fwd",#data,  # prepend "write stdin" command (0x06)
                response=True
            )

        asyncio.create_task(async_send(data))

    async def set_rx_method(self):
        def handle_rx(_, data: bytearray):
            if data[0] == 0x01:  # "write stdout" event (0x01)
                payload = data[1:]

                if payload == b"rdy":
                    self.ready_event.set()
                else:
                    print("Received:", payload)

        await self.client.start_notify(PYBRICKS_COMMAND_EVENT_CHAR_UUID, handle_rx)

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
                self.client = client
            else:
                print("Connection to", hub_name, "failed")

            await self.set_rx_method()

            print("Start the program on the hub now with the button.")

        asyncio.create_task(async_connect_to())
