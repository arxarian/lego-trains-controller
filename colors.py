from pybricks.parameters import Color

def decodeHSV(hsv):
    #print(hsv)
    hue = hsv.h
    saturation = hsv.s
    value = hsv.v
    if value < 20 and saturation < 40:
        return Color.BLACK
    elif (hue > 180 or hue < 240) and value > 50 and value < 70 and saturation < 30:
        return Color.GRAY
    elif (hue > 340 or hue < 20) and value > 70 and value < 90:
        return Color.RED
    elif (hue > 30 and hue < 70) and value > 80 and saturation > 60:
        return Color.YELLOW
    elif (hue > 200 and hue < 250) and value > 35 and saturation > 80:
        return Color.BLUE
    elif (hue > 100 and hue < 150) and value > 35:
        return Color.GREEN
    elif (hue > 340 or hue < 30) and value > 90:
        return Color.WHITE

    return Color.NONE