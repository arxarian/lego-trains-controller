from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Property
from PySide6.QtQml import QmlElement
from PySide6.QtGui import QColor


QML_IMPORT_NAME = "TrainView"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class PathIndicator(QObject):

    def __init__(self, data: dict=None, parent=None):
        super().__init__(parent)
        self._visible = True    # TODO - change to false
                                #
        self._color = "red"     # TODO - no color setting at creation, it should be set when visible true?
                                #      - what about for more indicators?

        self._x = 0             # set in load_metadata
        self._y = 0             # set in load_metadata
        self._path_id = None    # set in load_metadata

        self.load_metadata(data)

        print("PathIndicator created", self._x, self._y, self._path_id)

    def load_metadata(self, data):
        if data == None:
            return

        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def visible(self):
        return self._visible

    def set_visible(self, value):
        # set color if true
        self._visible = value
        self.visible_changed.emit()

    visible_changed = Signal()
    visible = Property(bool, visible, set_visible, notify=visible_changed)

    def color(self):
        return self._color

    def set_color(self, value):
        self._color = value
        self.color_changed.emit()

    color_changed = Signal()
    color = Property(QColor, color, set_color, notify=color_changed)

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

    def path_id(self):
        return self._path_id

    def set_path_id(self, value):
        self._path_id = value
        self.path_id_changed.emit()

    path_id_changed = Signal()
    path_id = Property(str, path_id, set_path_id, notify=path_id_changed)
