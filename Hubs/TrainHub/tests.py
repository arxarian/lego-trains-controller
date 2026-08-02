from pybricks.pupdevices import DCMotor, ColorDistanceSensor
from pybricks.parameters import Button, Color, Direction, Port, Side, Stop
from pybricks.robotics import DriveBase
from pybricks.tools import wait, StopWatch

import colors

sensor = ColorDistanceSensor(Port.B)
train_motor = DCMotor(Port.A)
direction = True

def highSpeed():
    train_motor.dc(30 if direction else -30)

def lowSpeed():
    train_motor.dc(30 if direction else -30)

def stop():
    train_motor.dc(0)
    wait(500)
    lowSpeed()
    wait(500)

lowSpeed()

while True:
    hsv = sensor.hsv()
    color = colors.decodeHSV(hsv)
    if color != Color.NONE:
        print(color, hsv)


    if color == Color.RED:
        direction = False
        stop()
    elif color == Color.YELLOW:
        direction = True
        stop()

    lowSpeed()

    wait(10)
