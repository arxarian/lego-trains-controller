from pybricks.pupdevices import DCMotor, ColorDistanceSensor
from pybricks.parameters import Port, Color
from pybricks.tools import wait
from pybricks.hubs import CityHub

# Standard MicroPython modules
from usys import stdin, stdout
from uselect import poll

import colors

hub = CityHub()
train_motor = DCMotor(Port.A)
sensor = ColorDistanceSensor(Port.B)

# Optional: Register stdin for polling. This allows
# you to wait for incoming data without blocking.
keyboard = poll()
keyboard.register(stdin)

stdout.buffer.write(b"int")
wait(10) # wait 10 ms for the int command to be sent

while True:

    # Let the remote program know we are ready for a command.
    stdout.buffer.write(b"rdy")

    lastColor = Color.NONE
    lastSentColor = Color.NONE

    # Optional: Check available input.
    while not keyboard.poll(0):
        # Optional: Do something here.
        hsv = sensor.hsv()
        color = colors.decodeHSV(hsv)
        if color == lastColor and color != lastSentColor:
            lastSentColor = color
            strColor = str(color).split('.')[-1]
            stdout.buffer.write(b"clr" + bytes(strColor, "utf-8"))

        lastColor = color

        wait(10)

    # Read three bytes.
    cmd = stdin.buffer.read(3)

    # Decide what to do based on the command.
    if cmd == b"fwd":
        speed = int.from_bytes(stdin.buffer.read(2), 'big')
        train_motor.dc(speed)
    elif cmd == b"rev":
        speed = int.from_bytes(stdin.buffer.read(2), 'big')
        train_motor.dc(-speed)
    elif cmd == b"bye":
        break
    elif cmd == b"sht":
        hub.system.shutdown()
    elif cmd == b"vol":
        stdout.buffer.write(b"vol" + hub.battery.voltage().to_bytes(2, 'big'))
    else:
        train_motor.stop()
