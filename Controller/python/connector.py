from __future__ import annotations

from enum import IntEnum
from PySide6.QtCore import QObject, Property, Signal, QEnum
from PySide6.QtQml import QmlElement
from rotator import Rotator

QML_IMPORT_NAME = "TrainView"
QML_IMPORT_MAJOR_VERSION = 1

@QEnum
class State(IntEnum):
    NotConnected = -1

@QmlElement
class Connector(QObject):
    QEnum(State)

    def __init__(self, data: dict=None, name: str="", connectedRailId: int=State.NotConnected,
        parent=None):

        super().__init__(parent)
        self._name = name
        self._dir = str()
        self._angle = 0
        self._rotator = None
        self._next = 0

        self._connectedRailId = connectedRailId     # not defined in json
        self._visible = not self.connected()        # not defined in json

        self.load_metadata(data)

    def load_metadata(self, data):
        if data == None:
            return

        for key, value in data.items():
            if hasattr(self, key):
                if key == "rotator":
                    self._rotator = Rotator.load_data(value, self)
                    continue
                setattr(self, key, value)

    def save_data(self):
        return {"name": self._name, "connectedRailId": self._connectedRailId}

    def load_data(data, parent):
        return Connector(name=data.get("name", str()),
            connectedRailId=data.get("connectedRailId", State.NotConnected), parent=parent)

    def connected(self):
        return self._connectedRailId != State.NotConnected

    def angle(self):
        return self._angle

    def set_angle(self, value):
        self._angle = value
        self.angle_changed.emit()

    angle_changed = Signal()
    angle = Property(float, angle, set_angle, notify=angle_changed)

    def name(self):
        return self._name

    def set_name(self, value):
        self._name = value
        self.name_changed.emit()

    name_changed = Signal()
    name = Property(str, name, set_name, notify=name_changed)

    def dir(self):
        return self._dir

    def set_dir(self, value):
        self._dir = value
        self.dir_changed.emit()

    dir_changed = Signal()
    dir = Property(str, dir, set_dir, notify=dir_changed)

    def rotator(self):
        return self._rotator

    def set_rotator(self, value):
        self._rotator = value
        self.rotator_changed.emit()

    rotator_changed = Signal()
    rotator = Property(Rotator, rotator, set_rotator, notify=rotator_changed)

    def next(self):
        return self._next

    def set_next(self, value):
        self._next = value
        self.next_changed.emit()

    next_changed = Signal()
    next = Property(int, next, set_next, notify=next_changed)

    def visible(self):
        return self._visible

    def set_visible(self, value):
        self._visible = value
        self.visible_changed.emit()

    visible_changed = Signal()
    visible = Property(bool, visible, set_visible, notify=visible_changed)

    def connectedRailId(self):
        return self._connectedRailId

    def set_connectedRailId(self, value):
        self._connectedRailId = value
        self.connectedRailId_changed.emit()
        self.set_visible(not self.connected())

    connectedRailId_changed = Signal()
    connectedRailId = Property(int, connectedRailId, set_connectedRailId, notify=connectedRailId_changed)
