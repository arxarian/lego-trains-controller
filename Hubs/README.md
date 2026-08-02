# Hub firmwares (Pybricks / MicroPython)

CityHub programs that talk to the LEGO Trains Controller over BLE.

| Folder / entry script | Role | Purpose |
|---|---|---|
| [`TrainHub/train_main.py`](TrainHub/train_main.py) | `train` | Drive motor + color sensor |
| [`SwitchHub/switch_main.py`](SwitchHub/switch_main.py) | `switch` | Throw a turnout (position A/B) |

Entry scripts use unique names (`train_main` / `switch_main`) so both can exist in [Pybricks Code](https://code.pybricks.com/) without colliding on `main.py`. Open the matching file, connect the hub, download/run.

## Framing

Same Pybricks GATT characteristic as the host (`c5f50002-8280-46da-89f4-6d8051e4aeef`):

| Direction | Format |
|---|---|
| Host → hub | Write: `0x06` + 3-byte command + optional data |
| Hub → host | Notify: `0x01` + payload (hub writes via `stdout.buffer`) |

Hub programs use stdin/stdout; the host wraps commands with `0x06` and strips the `0x01` event prefix.

## Shared commands / payloads

**Hub → host**

| Payload | Meaning |
|---|---|
| `int` | Program started |
| `rol` + role | Role handshake: trailing ASCII `train` or `switch` (F3) |
| `rdy` | Ready for next host command |
| `vol` + 2 bytes | Battery voltage (big-endian uint16) |
| `clr` + name | Color reading (train only) |
| `pos` + `A`\|`B` | Position ack (switch only) |

**Host → hub**

| Command | Data | Meaning |
|---|---|---|
| `bye` | — | Disconnect / exit loop |
| `sht` | — | Hub shutdown |
| `vol` | — | Request voltage |
| `fwd` / `rev` | 2-byte speed | Train motor (train only) |
| `pos` | 1 byte `A` or `B` | Set turnout (switch only) |

## Role handshake (F3)

After BLE connect, the user starts the hub program (hub button). The hub must send:

1. `int`
2. `rol` + `train` **or** `rol` + `switch`

The Controller waits for a known role before appending the hub to `TrainDevices` or `SwitchDevices`. Unknown role or timeout → disconnect; the host never invents a role.

Discover UI does not ask the user to pick train vs switch.
