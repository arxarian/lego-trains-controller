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

RailSource = {
  RailType.Straight: "StraightTrackPiece.qml",
  RailType.Curved: "CurvedTrackPiece.qml",
  RailType.Switch: "SwitchTrackPiece.qml"
}

@QmlElement
class Rail(QObject):
    last_id = 0  # static variable
    QEnum(RailType)

    @Slot(result=str)
    def source(self) -> str:
        return RailSource[self._type]


    def generateId():   # static method
        Rail.last_id += 1
        return Rail.last_id

    # ✓ id
    # ✓ type
    #   length
    # ✓ rotation (move together with rotation center?)
    # ½ position
    #   - x
    #   - y
    # ½ rotation center
    #   - x
    #   - y
    #   ports
    #   - port
    #     - rotation center
    #       - x
    #       - y
    #     - sibling [id, None]
    #     - dir (straight, left, right)
    #     - possible routes (e.g. the switch rail is limited)
    #   markers
    #   - color
    #   - rotation
    #   - position
    #     - x
    #     - y
    #   - rotation center
    #     - x
    #     - y

    def __init__(self, type: RailType, parent=None):
        super().__init__(parent)
        self._id = Rail.generateId()    # int
        self._type = type               # RailType

        self._rotation = 0              # float
        self._x = 0                     # float
        self._y = 0                     # float
        self._rotation_x = 0            # float
        self._rotation_y = 0            # float
        self._connected_to = {}         # dict

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

    def rotation_x(self):
        return self._rotation_x

    def set_rotation_x(self, value):
        self._rotation_x = value
        self.rotation_x_changed.emit()

    rotation_x_changed = Signal()
    rotation_x = Property(float, rotation_x, set_rotation_x, notify=rotation_x_changed)

    def rotation_y(self):
        return self._rotation_y

    def set_rotation_y(self, value):
        self._rotation_y = value
        self.rotation_y_changed.emit()

    rotation_y_changed = Signal()
    rotation_y = Property(float, rotation_y, set_rotation_y, notify=rotation_y_changed)
