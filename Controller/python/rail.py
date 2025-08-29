from __future__ import annotations

import json
from enum import IntEnum
from PySide6.QtCore import QObject, Slot, Property, Signal, QEnum, QAbstractListModel
from PySide6.QtQml import QmlElement

from connectors import Connectors
from rotator import Rotator

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

    def generate_id(id):   # static method
        if id == 0:
            Rail.last_id += 1
            return Rail.last_id
        else:
            return id

    # ✓ id
    # ✓ type
    # ✓ length
    # ½ position - not in a container
    #   - x
    #   - y
    # ✓ rotator
    #   - angle
    #   - x
    #   - y
    #   connectors
    #   - connector
    # ½   - rotator - TODO: rotator is not used
    #       - angle
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
    #   - rotator
    #     - angle
    #     - x
    #     - y

    def __init__(self, type=RailType.Undefined, id=0, length=0, x=0, y=0, rotator=None, parent=None):

        super().__init__(parent)
        self._id = Rail.generate_id(id)             # int
        self._source = str()                        # str
        self._type = type                           # RailType
        self._length = length                       # int   // TODO - for switch, there can be different lenghts

        self._x = x                                 # float
        self._y = y                                 # float

        self._rotator = rotator                     # Rotator
        if rotator == None:
            self._rotator = Rotator(parent=self)

        self._connectors = Connectors(parent=self)  # QAbstractListModel

        self._connected_to = [] #{}                 # change it to dict later   // TODO - move to connectors?
        self._to_index = 0                          # int                       // TODO - move to connectors?
        self._from_index = 0                        # int

        self.load_metadata()

        # if self._type == RailType.Straight or self._type == RailType.Curved:
        #     self._ports = ["start", "end"]
        # elif self.type == RailType.SwitchLeft:
        #     self._ports = ["start", "left", "right"]
        # else:
        #     self._ports = []

        # for port in self._ports:
        #     self._connected_to[port] = None

    def load_metadata(self):
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

    def save_data(self):  # TODO - missing connected to!
        return {"id": self._id, "type": self._type, "rotator": self._rotator.save_data(),
            "from_index": self._from_index, "to_index": self._to_index, "x": self._x, "y": self._y}

    def load_data(data, parent):
        return Rail(type=data.get("type", ""), id=data.get("id", ""),
            rotator=Rotator.load_data(data.get("rotator", {}), parent),
            x=data.get("x", 0), y=data.get("y", 0), parent=parent)

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

    def length(self):
        return self._length

    def set_length(self, value):
        self._length = value
        self.length_changed.emit()

    length_changed = Signal()
    length = Property(int, length, set_length, notify=length_changed)

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

    def rotator(self):
        return self._rotator

    def set_rotator(self, value):
        self._rotator = value
        self.rotator_changed.emit()

    rotator_changed = Signal()
    rotator = Property(Rotator, rotator, set_rotator, notify=rotator_changed)

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
