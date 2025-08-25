from __future__ import annotations

import json
from enum import IntEnum
from PySide6.QtCore import QObject, Slot, Property, Signal, QEnum, QAbstractListModel
from PySide6.QtQml import QmlElement

from connectors import Connectors

QML_IMPORT_NAME = "TrainView"
QML_IMPORT_MAJOR_VERSION = 1

@QEnum
class RailType(IntEnum):
    Undefined = -1
    Straight = 0
    Curved = 1
    SwitchLeft = 2
    SwitchRight = 3

RailSource = {
    RailType.Straight: "straight.json",
    RailType.Curved: "curved.json",
    RailType.SwitchLeft: "switch left.json",
    RailType.SwitchRight: "switch right.json"
}

@QmlElement
class Rail(QObject):
    last_id = 0  # static variable
    QEnum(RailType)

    def generateId(id):   # static method
        if id == 0:
            Rail.last_id += 1
            return Rail.last_id
        else:
            return id

    # ✓ id
    # ✓ type
    #   length
    # ✓ rotation (move together with rotation center?)
    # ½ position
    #   - x
    #   - y
    # ½ rotation center - is it even needed?
    #   - x
    #   - y
    #   ports
    #   - port
    #     - rotation center
    #       - rotation?
    #       - x
    #       - y
    #     - sibling [id, None]
    #     - dir (straight, left, right)
    #     - possible routes (e.g. the switch rail is limited)
    #   markers
    #   - color
    #   - position
    #     - x
    #     - y
    #   - rotation center
    #     - rotation
    #     - x
    #     - y

    def __init__(self, type=RailType.Undefined, id=0, angle=0, x=0, y=0,
        rotation_x=0, rotation_y=0, parent=None):

        super().__init__(parent)
        self._id = Rail.generateId(id)  # int
        self._source = ""               # str
        self._type = type               # RailType

        self._angle = angle       # float
        self._x = x                     # float
        self._y = y                     # float
        self._rotation_x = rotation_x   # float
        self._rotation_y = rotation_y   # float

        self._connectors = Connectors()  # QAbstractListModel
        self._connected_to = [] #{}         # change it to dict later   // TODO - move to connectors?
        self._to_index = 0              # int                           // TODO - move to connectors?
        self._from_index = 0

        self.load_metadata_from_Json()

        # if self._type == RailType.Straight or self._type == RailType.Curved:
        #     self._ports = ["start", "end"]
        # elif self.type == RailType.SwitchLeft:
        #     self._ports = ["start", "left", "right"]
        # else:
        #     self._ports = []

        # for port in self._ports:
        #     self._connected_to[port] = None

    def load_metadata_from_Json(self):
        if self._type == RailType.Undefined:
            print("undefined rail type")
            return

        with open("resources/" + RailSource[self._type]) as json_data:
            data = json.load(json_data)
            for key, value in data.items():
                if hasattr(self, key):
                    if key == "connectors":
                        self._connectors.setModel(value)
                        continue
                    setattr(self, key, value)

    def to_dict(self):  # TODO - missing connected to!
        return {"id": self._id, "type": self._type, "angle": self._angle,
            "from_index": self._from_index, "to_index": self._to_index, "x": self._x,
            "y": self._y, "rotation_x": self._rotation_x, "rotation_y": self._rotation_y}

    def from_dict(data):
        return Rail(type=data.get("type", ""), id=data.get("id", ""), angle=data.get("angle", 0),
            x=data.get("x", 0), y=data.get("y", 0), rotation_x=data.get("rotation_x", 0),
            rotation_y=data.get("rotation_y", 0))

    def id(self):
        return self._id

    def set_id(self, value):
        self._id = value
        self.id_changed.emit()

    id_changed = Signal()
    id = Property(int, id, set_id, notify=id_changed)

    def source(self):
        return self._source

    def set_source(self, value):
        self._source = value
        self.source_changed.emit()

    source_changed = Signal()
    source = Property(str, source, set_source, notify=source_changed)

    def connectors(self):
        return self._connectors

    connectors = Property(QObject, connectors, constant=True)

    def type(self):
        return self._type

    def set_type(self, value):
        self._type = value
        self.type_changed.emit()

    type_changed = Signal()
    type = Property(int, type, set_type, notify=type_changed)

    def angle(self):
        return self._angle

    def set_angle(self, value):
        self._angle = value
        self.angle_changed.emit()

    angle_changed = Signal()
    angle = Property(float, angle, set_angle, notify=angle_changed)

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

    def from_index(self):
        return self._from_index

    def set_from_index(self, value):
        self._from_index = value
        self.from_index_changed.emit()

    from_index_changed = Signal()
    from_index = Property(float, from_index, set_from_index, notify=from_index_changed)

    def to_index(self):
        return self._to_index

    def set_to_index(self, value):
        self._to_index = value
        self.to_index_changed.emit()

    to_index_changed = Signal()
    to_index = Property(int, to_index, set_to_index, notify=to_index_changed)

    def connected_to(self):
        return self._connected_to

    def append_connected_to(self, from_rail_id, from_index):
        self._connected_to.append(from_rail_id)
        self._from_index = from_index
        self.connected_to_changed.emit()
        self.from_index_changed.emit()

    connected_to_changed = Signal()
    connected_to = Property(list, connected_to, notify=connected_to_changed)
