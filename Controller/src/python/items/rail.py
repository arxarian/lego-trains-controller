from __future__ import annotations

import json
import webcolors
from enum import IntEnum
from importlib import resources
from PySide6.QtCore import QObject, Property, Signal, Slot, QEnum
from PySide6.QtQml import QmlElement

from python.items.rotator import Rotator
from python.models.connectors import Connectors
from python.models.markers import Markers
from python.models.path_indicators import PathIndicators

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

SWITCH_PATH_IDS = ("A", "B")
DEFAULT_SWITCH_POSITION = "A"


class ControlMode(IntEnum):
    Manual = 1
    Automatic = 2


@QmlElement
class Rail(QObject):
    last_id = 0  # static variable
    QEnum(RailType)
    QEnum(ControlMode)

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

    def __init__(self, type: RailType=RailType.Undefined, id: int=0, x: float=0, y: float=0,
    rotator: Rotator=None, connectors: Connectors=None, markers: Markers=None, parent=None):

        super().__init__(parent)
        self._id = Rail.generate_id(id)             # int
        self._source = str()                        # str
        self._type = type                           # RailType/Enum

        self._x = x                                 # float
        self._y = y                                 # float
        self._rotator = rotator if rotator is not None else Rotator(parent=self)    # Rotator/QObject

        # QAbstractListModels
        self._markers = markers if markers is not None else Markers(parent=self)
        self._connectors = connectors if connectors is not None else Connectors(parent=self)
        self._path_indicators = PathIndicators(parent=self)
        self._reservation_indicators = PathIndicators(parent=self)
        self._reserved = False  # reserved by train
        # Session-only logical turnout; mode/lock are not persisted (C2.2)
        self._switch_position = DEFAULT_SWITCH_POSITION
        self._control_mode = ControlMode.Manual
        self._locked_by = ""

        self._paths = {}                            # dictionary

        self.load_metadata()

        self._markers.rail = self
        self._markers._connectors = self._connectors
        self._connectors._markers = self._markers

        if self.is_switch():
            self._sync_path_id_active()

    @Slot(result=bool)
    def is_switch(self) -> bool:
        return self._type in (RailType.SwitchLeft, RailType.SwitchRight)

    def _sync_path_id_active(self) -> None:
        self._path_indicators.set_path_id_active(self._switch_position)

    def load_metadata(self):
        if self._type == RailType.Undefined:
            print("undefined rail type")
            return

        with resources.open_text("resources", RailSource[self._type]) as json_data:
            data = json.load(json_data)
            for key, value in data.items():
                if hasattr(self, key):
                    if key == "connectors":
                        self._connectors.setModel(value)
                        continue
                    if key == "markers":
                        self._markers.setModel(value)
                        continue
                    if key == "path_indicators":
                        self._path_indicators.setModel(value)
                        continue
                    setattr(self, key, value)

    def save_data(self):  # TODO - why to save rotator? Is it needed?
        return {"id": self._id, "type": self._type, "rotator": self._rotator.save_data(),
            "x": round(self._x, 1), "y": round(self._y, 1), "connectors": self._connectors.save_data(),
            **({"markers": self._markers.save_data()} if self._markers.save_data() else {})}

    def load_data(data, parent=None):
        return Rail(type=data.get("type", RailType.Undefined), id=data.get("id", 0), x=data.get("x", 0),
            y=data.get("y", 0), rotator=Rotator.load_data(data.get("rotator", {}), parent),
            connectors=Connectors.load_data(data.get("connectors", []), parent),
            markers=Markers.load_data(data.get("markers", []), parent), parent=parent)

    def toString(self):
        ret = "id " + str(self.id) + " markers "
        for m in self.markers._items:
            if m.taken:
                ret = ret + webcolors.hex_to_name(m.color.name()) + " "
        return ret

    def id(self):
        return self._id

    def set_id(self, value):
        self._id = value
        self.id_changed.emit()

    id_changed = Signal()
    id = Property(int, id, set_id, notify=id_changed)

    def reserved(self):
        return self._reserved

    def set_reserved(self, value):
        self._reserved = value
        self.reserved_changed.emit()

    reserved_changed = Signal()
    reserved = Property(bool, reserved, set_reserved, notify=reserved_changed)

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

    def path_indicators(self):
        return self._path_indicators

    path_indicators = Property(QObject, path_indicators, constant=True)

    def reservation_indicators(self):
        return self._reservation_indicators

    reservation_indicators = Property(QObject, reservation_indicators, constant=True)

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

    def switch_position(self):
        return self._switch_position

    def set_switch_position(self, value):
        if not self.is_switch() or value not in SWITCH_PATH_IDS:
            return
        if self._switch_position == value:
            return
        self._switch_position = value
        self._sync_path_id_active()
        self.switch_position_changed.emit()

    switch_position_changed = Signal()
    switch_position = Property(str, switch_position, set_switch_position, notify=switch_position_changed)

    def control_mode(self):
        return self._control_mode

    def set_control_mode(self, value):
        if not self.is_switch():
            return
        value = ControlMode(int(value))
        if self._control_mode == value:
            return
        self._control_mode = value
        self.control_mode_changed.emit()

    control_mode_changed = Signal()
    control_mode = Property(int, control_mode, set_control_mode, notify=control_mode_changed)

    def locked(self):
        return bool(self._locked_by)

    locked_changed = Signal()
    locked = Property(bool, locked, notify=locked_changed)

    def locked_by(self):
        return self._locked_by

    locked_by_changed = Signal()
    locked_by = Property(str, locked_by, notify=locked_by_changed)

    def lock_for(self, owner):
        if not self.is_switch() or not owner:
            return
        if self._locked_by == owner:
            return
        self._locked_by = owner
        self.locked_changed.emit()
        self.locked_by_changed.emit()

    def unlock_for(self, owner):
        if not self.is_switch() or not owner:
            return
        if self._locked_by != owner:
            return
        self.unlock()

    def unlock(self):
        if not self._locked_by:
            return
        self._locked_by = ""
        self.locked_changed.emit()
        self.locked_by_changed.emit()

    @Slot(str)
    def setSwitchPosition(self, path_id):
        self.set_switch_position(path_id)

    @Slot()
    def toggleSwitchPosition(self):
        if not self.is_switch():
            return
        if self._locked_by:
            print(f"Rail {self._id}: switch toggle rejected (locked by {self._locked_by})")
            return
        if self._control_mode != ControlMode.Manual:
            print(f"Rail {self._id}: switch toggle rejected (Automatic mode)")
            return
        self.set_switch_position("B" if self._switch_position == "A" else "A")

    def reserve_segment(self, path_id, from_d, to_d):
        pts = [{"x": p.x, "y": p.y} for p in self._path_indicators._items
               if p.path_id in ("", path_id) and from_d <= p.distance <= to_d]
        self._reservation_indicators.setModel(pts)

    def unreserve_segment(self, path_id, from_d, to_d):
        self._reservation_indicators.clear()

    def connectTo(self, fromRailId, fromIndex):
        self._connectors.connectTo(fromRailId, fromIndex)
        self._markers.updateStates()

    def disconnectFrom(self, fromRailId):
        self._connectors.disconnectFrom(fromRailId)
        self._markers.updateStates()

    @Slot(result=QObject)
    def setNextConnector(self):
        connector = self._connectors.setNextConnector()
        return connector
