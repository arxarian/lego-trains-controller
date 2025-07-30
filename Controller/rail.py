from __future__ import annotations

from enum import IntEnum
from PySide6.QtCore import QObject, Slot, Property, Signal
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "TrainsView"
QML_IMPORT_MAJOR_VERSION = 1

class RailType(IntEnum):
    Unknown = -1
    Straight = 0
    Curved = 1
    Switch = 2

@QmlElement
class Rail(QObject):

    # id, pointer, index
    # type
    # flipped
    # siblings / connecting slots
    # length
    # possible routes (e.g. the switch rail is limited)
    # position x, y
    # rotation

    def __init__(self, index: int, type: RailType, flipped: bool, rotation: float, x: float, y, float, parent=None):
        super().__init__(parent)
        self._index = index
        self._type = type
        self._flipped = flipped
        self._rotation = rotation
        self._x = x
        self._y = y

        if self._type == RailType.Straight or self._type == RailType.Curved:
            self._ports = ["start", "end"]
        elif self.type == RailType.Switch:
            self._ports = ["start", "left", "right"]
        else:
            self._ports = []

        for port in self._ports:
            self._connected_to[port] = None
