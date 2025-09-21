from __future__ import annotations

from PySide6.QtQml import QmlElement
from rotator import Rotator

QML_IMPORT_NAME = "TrainView"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class Marker(Rotator):

    def __init__(self, data: dict=None, x: float=0, y: float=0, angle: float=0, parent=None):
        # get the data if any are defined
        x = data.get("x", x)
        y = data.get("y", y)
        angle = data.get("angle", angle)

        # call the parent's ctor
        super().__init__(x, y, angle, parent)

