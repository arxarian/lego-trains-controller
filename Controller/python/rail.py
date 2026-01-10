from __future__ import annotations

import json
import webcolors
from enum import IntEnum
from PySide6.QtCore import QObject, Property, Signal, QEnum
from PySide6.QtQml import QmlElement

from connectors import Connectors
from markers import Markers
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
            Rail.last_id = max(Rail.last_id, id)
            return id

    # ✓ id
    # ✓ type
    # ½ position - not in a container
    # ✓ - x
    # ✓ - y
    # ✓ rotator
    # ✓ - angle
    # ✓ - x
    # ✓ - y
    # ✓ connectors
    # ✓ - connector
    # ✓   - sibling [id, -1]
    # ✓   - rotator
    # ✓     - angle
    # v     - x
    # ✓     - y
    # ½ possible paths (e.g. the switch rail is limited)
    # ✓ - lenghts
    # ✓ - paths
    # ✓ markers
    # ✓ - color
    # ✓ - position
    # ✓   - x
    # ✓   - y
    # ✓ - rotator
    # ✓   - angle
    # ✓   - x
    # ✓   - y

    def __init__(self, type: RailType=RailType.Undefined, id: int=0, length: int=0, x: float=0,
        y: float=0, rotator: Rotator=None, connectors: Connectors=None, markers: Markers=None,
        parent=None):

        super().__init__(parent)
        self._id = Rail.generate_id(id)             # int
        self._source = str()                        # str
        self._type = type                           # RailType/Enum

        self._x = x                                 # float
        self._y = y                                 # float
        self._rotator = rotator if rotator is not None else Rotator(parent=self)    # Rotator/QObject
        self._markers = markers if markers is not None else Markers(parent=self)    # QAbstractListModel
        self._connectors = connectors if connectors is not None else Connectors(parent=self)    # QAbstractListModel

        self._paths = {}                            # dictionary

        self.load_metadata()

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
                    if key == "markers":
                        self._markers.setModel(value)
                        continue
                    setattr(self, key, value)

    def save_data(self):  # TODO - why to save rotator? Is it needed?
        return {"id": self._id, "type": self._type, "rotator": self._rotator.save_data(),
            "x": round(self._x, 1), "y": round(self._y, 1), "connectors": self._connectors.save_data(),
            **({"markers": self._markers.save_data()} if self._markers.save_data() else {})}

    def load_data(data, parent):
        return Rail(type=data.get("type", 0), id=data.get("id", 0), x=data.get("x", 0), y=data.get("y", 0),
            rotator=Rotator.load_data(data.get("rotator", {}), parent),
            connectors=Connectors.load_data(data.get("connectors", []), parent),
            markers=Markers.load_data(data.get("markers", []), parent), parent=parent)

    def toString(self):
        ret = "id " + str(self.id) + " markers "
        for m in self.markers._items:
            if m.visible:
                ret = ret + webcolors.hex_to_name(m.color.name()) + " "
        return ret

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

    def markers(self):
        return self._markers

    markers = Property(QObject, markers, constant=True)

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

    def paths(self):
        return self._paths

    def set_paths(self, value):
        self._paths = value
        self.paths_changed.emit()

    paths_changed = Signal()
    paths = Property(list, paths, set_paths, notify=paths_changed)

    def connectTo(self, fromRailId, fromIndex):
        self._connectors.connectTo(fromRailId, fromIndex)

    def disconnectFrom(self, fromRailId):
        self._connectors.disconnectFrom(fromRailId)
