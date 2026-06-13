from __future__ import annotations

from enum import IntEnum, auto
from PySide6.QtCore import QObject, Signal, Property, Slot, QPointF, QEnum
from PySide6.QtQml import QmlElement
from PySide6.QtGui import QColor

from python.items.rotator import Rotator

QML_IMPORT_NAME = "TrainView"
QML_IMPORT_MAJOR_VERSION = 1

@QEnum
class MarkerState(IntEnum):
    Undefined = auto()
    Free = auto()
    Taken = auto()
    Blocked = auto()

@QmlElement
class Marker(QObject):
    QEnum(MarkerState)

    def __init__(self, data: dict=None, color=None, index=-1, parent=None):
        super().__init__(parent)
        self._state = MarkerState.Taken if color else MarkerState.Free
        self._index = index
        self._color = color
        self._rotator = None    # set in load_metadata
        self._distance = 0      # set in load_metadata
        self._path_id = None    # set in load_metadata
        self._position = QPointF()
        self._connector = None

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
        if self._color is not None:
            return { "index": self._index, "color": self._color.name() }

    @Slot()
    def remove(self):
        self.set_color(None)
        self.set_state(MarkerState.Free)

        parent = self.parent()
        parent.updateStates()

    def position(self):
        return self._position

    def set_position(self, value):
        self._position = value
        self.position_changed.emit()

    position_changed = Signal()
    position = Property(QPointF, position, set_position, notify=position_changed)

    def free(self):
        return self._state == MarkerState.Free

    free_changed = Signal()
    free = Property(int, free, notify=free_changed)

    def taken(self):
        return self._state == MarkerState.Taken

    taken_changed = Signal()
    taken = Property(int, taken, notify=taken_changed)

    def blocked(self):
        return self._state == MarkerState.Blocked

    blocked_changed = Signal()
    blocked = Property(int, blocked, notify=blocked_changed)

    @Slot(QColor)
    def take(self, value):
        self.set_color(value)
        self.set_state(MarkerState.Taken)

        parent = self.parent()
        parent.updateStates()

    def state(self):
        return self._state

    def set_state(self, value):
        if self._state != value:
            self._state = value
            self.state_changed.emit()
            self.taken_changed.emit()   # TODO - no guard
            self.free_changed.emit()    # TODO - no guard
            self.blocked_changed.emit() # TODO - no guard

            #parent = self.parent()
            #parent.updateStates()
            #parent.updateConnectedRailsEnabledStates()

    state_changed = Signal()
    state = Property(int, state, set_state, notify=state_changed)

    def color(self):
        return self._color

    def set_color(self, value):
        self._color = value
        self.color_changed.emit()

    color_changed = Signal()
    color = Property(QColor, color, set_color, notify=color_changed)

    def index(self):
        return self._index

    def set_index(self, value):
        self._index = value
        self.index_changed.emit()

    index_changed = Signal()
    index = Property(int, index, set_index, notify=index_changed)

    def rotator(self):
        return self._rotator

    rotator = Property(QObject, rotator, constant=True)

    def distance(self):
        return self._distance

    def set_distance(self, value):
        self._distance = value
        self.distance_changed.emit()

    distance_changed = Signal()
    distance = Property(int, distance, set_distance, notify=distance_changed)

    def path_id(self):
        return self._path_id

    def set_path_id(self, value):
        self._path_id = value
        self.path_id_changed.emit()

    path_id_changed = Signal()
    path_id = Property(str, path_id, set_path_id, notify=path_id_changed)

    def at_boundary(self):
        return self._connector != None

    def connector(self):
        return self._connector

    def set_connector(self, value):
        self._connector = value
        self.connector_changed.emit()

    connector_changed = Signal()
    connector = Property(str, connector, set_connector, notify=connector_changed)
