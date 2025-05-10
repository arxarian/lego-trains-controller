from pybricks.parameters import Color

def decodeHSV(hsv):
    print(hsv)
    hue = hsv.h
    value = hsv.v
    if (hue > 340 or hue < 20) and value < 90 and value > 70:
        return Color.RED
    elif (hue > 30 and hue < 70) and value > 80:
        return Color.YELLOW
    elif (hue > 200 and hue < 250) and value > 35:
        return Color.BLUE
    elif (hue > 100 and hue < 150) and value > 35:
        return Color.GREEN
    elif (hue > 340 or hue < 30) and value > 90:
        return Color.WHITE
    elif value < 20:
        return Color.BLACK
    #elif (hue > 340 or hue < 30) and value > 20 and value < 80:
    #    return Color.GRAY

    return Color.NONE