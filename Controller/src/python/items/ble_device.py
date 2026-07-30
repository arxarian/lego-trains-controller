# This Python file uses the following encoding: utf-8
from __future__ import annotations

import asyncio

PYBRICKS_COMMAND_EVENT_CHAR_UUID = "c5f50002-8280-46da-89f4-6d8051e4aeef"

class BleDevice:
    """BLE transport helper for Pybricks hubs (train HW now; switch hubs later)."""

    def __init__(self, client):
        self.client = client
        self.ready_event = asyncio.Event()

    def send(self, cmd, data=b"", response=True):
        async def async_send(cmd, data, response):
            await self.ready_event.wait()
            self.ready_event.clear()
            await self.client.write_gatt_char(
                PYBRICKS_COMMAND_EVENT_CHAR_UUID,
                b"\x06" + cmd.encode() + data,
                response=response,
            )

        asyncio.create_task(async_send(cmd, data, response))

    async def start_notify(self, callback):
        await self.client.start_notify(
            PYBRICKS_COMMAND_EVENT_CHAR_UUID, callback
        )

    async def disconnect_client(self):
        await self.client.disconnect()
