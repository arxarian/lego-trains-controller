# This Python file uses the following encoding: utf-8
from __future__ import annotations

import asyncio

PYBRICKS_COMMAND_EVENT_CHAR_UUID = "c5f50002-8280-46da-89f4-6d8051e4aeef"

# Pybricks command opcodes (GATT write payload first byte)
PBIO_CMD_STOP_USER_PROGRAM = 0x00
PBIO_CMD_START_USER_PROGRAM = 0x01
PBIO_CMD_WRITE_STDIN = 0x06


class BleDevice:
    """BLE transport helper for Pybricks hubs (train and switch)."""

    def __init__(self, client):
        self.client = client
        self.ready_event = asyncio.Event()

    def send(self, cmd, data=b"", response=True):
        async def async_send(cmd, data, response):
            await self.ready_event.wait()
            self.ready_event.clear()
            await self.client.write_gatt_char(
                PYBRICKS_COMMAND_EVENT_CHAR_UUID,
                bytes([PBIO_CMD_WRITE_STDIN]) + cmd.encode() + data,
                response=response,
            )

        asyncio.create_task(async_send(cmd, data, response))

    async def start_user_program(self):
        """Start the program already downloaded to the hub (no button press).

        Ignores failures when a program is already running (BUSY).
        """
        try:
            await self.client.write_gatt_char(
                PYBRICKS_COMMAND_EVENT_CHAR_UUID,
                bytes([PBIO_CMD_START_USER_PROGRAM]),
                response=True,
            )
        except Exception as exc:
            # Already running or transient BLE error — role wait still proceeds.
            print(f"start_user_program: {exc} (continuing)")

    async def start_notify(self, callback):
        await self.client.start_notify(
            PYBRICKS_COMMAND_EVENT_CHAR_UUID, callback
        )

    async def disconnect_client(self):
        await self.client.disconnect()
