import asyncio

from python.items.ble_device import (
    BleDevice,
    PBIO_CMD_START_USER_PROGRAM,
    PBIO_CMD_WRITE_STDIN,
)
from python.hub_connector import _role_from_stdout_payload


class _FakeClient:
    def __init__(self):
        self.writes = []

    async def write_gatt_char(self, uuid, data, response=True):
        self.writes.append((uuid, bytes(data), response))


def test_start_user_program_writes_opcode_01():
    client = _FakeClient()
    ble = BleDevice(client)

    asyncio.run(ble.start_user_program())

    assert len(client.writes) == 1
    _, payload, response = client.writes[0]
    assert payload == bytes([PBIO_CMD_START_USER_PROGRAM])
    assert payload != bytes([PBIO_CMD_WRITE_STDIN])
    assert response is True


def test_start_user_program_ignores_already_running():
    class _BusyClient:
        async def write_gatt_char(self, uuid, data, response=True):
            raise RuntimeError("BUSY")

    async def _run():
        ble = BleDevice(_BusyClient())
        await ble.start_user_program()  # must not raise

    asyncio.run(_run())


def test_role_from_coalesced_stdout():
    assert _role_from_stdout_payload(b"introltrain") == "train"
    assert _role_from_stdout_payload(b"introlswitch") == "switch"
    assert _role_from_stdout_payload(b"roltrainrdy") == "train"
    assert _role_from_stdout_payload(b"rdy") is None
