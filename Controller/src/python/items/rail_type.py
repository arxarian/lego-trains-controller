# This Python file uses the following encoding: utf-8

from PySide6.QtCore import QObject, Property, Signal
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "TrainView"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class RailType(QObject):

    def __init__(self, data: dict=None, parent=None):
        super().__init__(parent)

        self._name = str()
        self._source = str()

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

    def source(self):
        return self._source

    def set_source(self, value):
        self._source = value
        self.source_changed.emit()

    source_changed = Signal()
    source = Property(str, source, set_source, notify=source_changed)
