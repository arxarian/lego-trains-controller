from pybricks.pupdevices import DCMotor, ColorDistanceSensor
from pybricks.parameters import Button, Color, Direction, Port, Side, Stop
from pybricks.robotics import DriveBase
from pybricks.tools import wait, StopWatch

import colors

sensor = ColorDistanceSensor(Port.B)
#train_motor = DCMotor(Port.A)

#def stop():
#    train_motor.dc(0)

#def highSpeed():
#    train_motor.dc(40)

#def lowSpeed():
#    train_motor.dc(50)


#lowSpeed()

while True:

    if sensor.distance() < 15:
        color = colors.decodeHSV(sensor.hsv())
        if color != Color.NONE:
            print(color)

    wait(10)

#    if color == Color.RED:
#        stop()
#        wait(3000)
#    elif color == Color.GREEN:
#        highSpeed()
#    elif color == Color.YELLOW:
#        lowSpeed()

