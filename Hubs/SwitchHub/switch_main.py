from pybricks.pupdevices import DCMotor
from pybricks.parameters import Port
from pybricks.tools import wait
from pybricks.hubs import CityHub

from usys import stdin, stdout
from uselect import poll

# Tune for the physical turnout mechanism.
MOTOR_DC = 50
PULSE_MS = 300

hub = CityHub()
switch_motor = DCMotor(Port.A)

keyboard = poll()
keyboard.register(stdin)

stdout.buffer.write(b"int")
wait(10)
stdout.buffer.write(b"rolswitch")
wait(10)

current_position = b"A"


def set_position(letter):
    global current_position
    if letter == b"A":
        switch_motor.dc(MOTOR_DC)
    elif letter == b"B":
        switch_motor.dc(-MOTOR_DC)
    else:
        return
    wait(PULSE_MS)
    switch_motor.stop()
    current_position = letter
    stdout.buffer.write(b"pos" + current_position)
    wait(10)  # flush before next rdy (avoid coalesced pos+rdy notify)


while True:
    stdout.buffer.write(b"rdy")

    while not keyboard.poll(0):
        wait(10)

    cmd = stdin.buffer.read(3)

    if cmd == b"pos":
        letter = stdin.buffer.read(1)
        set_position(letter)
    elif cmd == b"bye":
        break
    elif cmd == b"sht":
        hub.system.shutdown()
    elif cmd == b"vol":
        stdout.buffer.write(b"vol" + hub.battery.voltage().to_bytes(2, "big"))
        wait(10)  # flush before next rdy (avoid coalesced vol+rdy notify)
    else:
        switch_motor.stop()
