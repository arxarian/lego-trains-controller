# This Python file uses the following encoding: utf-8

from PySide6.QtCore import QObject, Property, Signal
from PySide6.QtGui import QColor
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "TrainView"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class MarkerType(QObject):

    def __init__(self, data: dict=None, parent=None):
        super().__init__(parent)

        self._name = str()
        self._color = QColor

        self.load_metadata(data)

    def load_metadata(self, data):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def name(self):
        return self._name

    def set_name(self, value):
        self._name = value
        self.name_changed.emit()

    name_changed = Signal()
    name = Property(str, name, set_name, notify=name_changed)

    def color(self):
        return self._color

    def set_color(self, value):
        self._color = value
        self.color_changed.emit()

    color_changed = Signal()
    color = Property(QColor, color, set_color, notify=color_changed)
