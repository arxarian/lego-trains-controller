from pybricks.parameters import Color


def decodeHSV(hsv):
    """Map ColorDistanceSensor HSV to a marker color.

    Order matters (first match wins). White is high-V / low-S (hue ignored).
    Blue uses a wider hue band and a moderate saturation floor.
    """
    hue = hsv.h
    saturation = hsv.s
    value = hsv.v

    # BLACK — dark
    if value < 20:
        return Color.BLACK

    # WHITE — bright and unsaturated (do not gate on hue)
    if value >= 75 and saturation <= 35:
        return Color.WHITE

    # GRAY — mid brightness, very low saturation (after white so it does not steal)
    if value > 50 and value < 75 and saturation < 15:
        return Color.GRAY

    # RED — hue near 0/360, high saturation
    if (hue > 340 or hue < 20) and value > 70 and saturation > 70:
        return Color.RED

    # YELLOW
    if hue > 30 and hue < 70 and value > 80 and saturation > 60:
        return Color.YELLOW

    # GREEN — slightly widened hue vs older decoder
    if hue > 100 and hue < 160 and value > 35 and saturation > 30:
        return Color.GREEN

    # BLUE — wider hue, lower saturation floor than the old s>80 gate
    if hue > 190 and hue < 260 and value >= 25 and saturation >= 40:
        return Color.BLUE

    return Color.NONE
