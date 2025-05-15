from __future__ import annotations

import sys

from PySide6.QtCore import QObject, Slot #Property, Signal

import asyncio
from bleak import BleakScanner, BleakClient

PYBRICKS_COMMAND_EVENT_CHAR_UUID = "c5f50002-8280-46da-89f4-6d8051e4aeef"

class Devices(QObject):

    def __init__(self, parent=None):
        super().__init__(parent)

    @Slot(str)
    def connect_to(self, hub_name):
        print("Wanna connect to", hub_name)

        async def async_connect_to():
            device = await BleakScanner.find_device_by_name(hub_name)

            if device is None:
                print(f"could not find hub with name: {hub_name}")
                return

            print("Found", hub_name)

            ready_event = asyncio.Event()

            def handle_rx(_, data: bytearray):
                if data[0] == 0x01:  # "write stdout" event (0x01)
                    payload = data[1:]

                    if payload == b"rdy":
                        ready_event.set()
                    else:
                        print("Received:", payload)

                # Connect to the hub.
            async with BleakClient(device) as client:   # TOOD add handle disconnect
                # Subscribe to notifications from the hub.
                await client.start_notify(PYBRICKS_COMMAND_EVENT_CHAR_UUID, handle_rx)

                # Shorthand for sending some data to the hub.
                async def send(data):
                    await ready_event.wait()
                    ready_event.clear()

                    # Send the data to the hub.
                    await client.write_gatt_char(
                        PYBRICKS_COMMAND_EVENT_CHAR_UUID,
                        b"\x06" + data,  # prepend "write stdin" command (0x06)
                        response=True
                    )

                # Tell user to start program on the hub.
                print("Start the program on the hub now with the button.")

                await send(b"fwd")
                await asyncio.sleep(1)
                await send(b"stp")


        asyncio.create_task(async_connect_to())
