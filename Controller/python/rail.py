from __future__ import annotations

from enum import IntEnum
from PySide6.QtCore import QObject, Slot, Property, Signal, QEnum
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "TrainView"
QML_IMPORT_MAJOR_VERSION = 1

@QEnum
class RailType(IntEnum):
    Unknown = -1
    Straight = 0
    Curved = 1
    Switch = 2

@QmlElement
class Rail(QObject):
    last_id = 0  # static variable
    QEnum(RailType)

    def generateId():   # static method
        Rail.last_id += 1
        return Rail.last_id

    # id, pointer, index
    # type
    # flipped
    # siblings / connecting slots
    # length
    # possible routes (e.g. the switch rail is limited)
    # position x, y
    # rotation

    def __init__(self, type: RailType, rotation: float=0, x: float=0, y: float=0, parent=None):
        super().__init__(parent)
        self._id = Rail.generateId()
        self._type = type
        self._rotation = rotation
        self._x = x
        self._y = y
        self._connected_to = {} # dict

        if self._type == RailType.Straight or self._type == RailType.Curved:
            self._ports = ["start", "end"]
        elif self.type == RailType.Switch:
            self._ports = ["start", "left", "right"]
        else:
            self._ports = []

        for port in self._ports:
            self._connected_to[port] = None

    def id(self):
        return self._id

    def set_id(self, value):
        self._id = value
        self.id_changed.emit()

    id_changed = Signal()
    id = Property(int, id, set_id, notify=id_changed)

    def type(self):
        return self._type

    def set_type(self, value):
        self._type = value
        self.type_changed.emit()

    type_changed = Signal()
    type = Property(int, type, set_type, notify=type_changed)

    def rotation(self):
        return self._rotation

    def set_rotation(self, value):
        self._rotation = value
        self.rotation_changed.emit()

    rotation_changed = Signal()
    rotation = Property(float, rotation, set_rotation, notify=rotation_changed)

    def x(self):
        return self._x

    def set_x(self, value):
        self._x = value
        self.x_changed.emit()

    x_changed = Signal()
    x = Property(float, x, set_x, notify=x_changed)

    def y(self):
        return self._y

    def set_y(self, value):
        self._y = value
        self.y_changed.emit()

    y_changed = Signal()
    y = Property(float, y, set_y, notify=y_changed)
