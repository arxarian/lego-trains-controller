# This Python file uses the following encoding: utf-8

from pathlib import Path
from dataclasses import dataclass, field

from PySide6.QtCore import QObject, Signal, Property

from rail import Rail
from rails import Rails
from connectorregister import ConnectorRegister

@dataclass
class Settings:
    canvas_position: dict=field(default_factory={"x": 0, "y": 0})
    zoom: float=1

class Project(QObject):
    def __init__(self, name: str="", data: dict=None, parent=None):
        super().__init__(parent)
        self._named = False
        self._connectorRegister = ConnectorRegister(self)
        self._rails = Rails(self._connectorRegister, self)
        self._settings = Settings

        if data:
            self._rails.load_data([Rail.from_dict(d) for d in data.get("rails", [])])
            self._settings = Settings.from_dict(data.get("settings", {}))

        self.set_name(name)

    def data(self) -> dict:
        return {
            "rails": [self._rails.to_dict() for rail in self._rails],
            "settings": self._settings.to_dict() if self._settings else {}
        }

    def name(self):
        return self._name

    def set_name(self, value):
        self._name = value
        self._path = Path(self._name + ".json") if self._name else Path()
        self.name_changed.emit()

        self.set_named(self._name != str())

    name_changed = Signal()
    name = Property(str, name, set_name, notify=name_changed)

    def named(self):
        return self._named

    def set_named(self, value):
        self._named = value
        self.named_changed.emit()

    named_changed = Signal()
    named = Property(str, named, set_named, notify=named_changed)

    def path(self):
        return self._path

    def set_path(self, value):
        self._path = value
        self.path_changed.emit()

    path_changed = Signal()
    path = Property(Path, path, set_path, notify=path_changed)

    def connectorRegister(self):
        return self._connectorRegister

    def set_connectorRegister(self, value):
        self._connectorregister = value
        self.connectorRegister_changed.emit()

    connectorRegister_changed = Signal()
    connectorRegister = Property(QObject, connectorRegister, set_connectorRegister, notify=connectorRegister_changed)

    def rails(self):
        return self._rails

    def set_rails(self, value):
        self._rails = value
        self.rails_changed.emit()

    rails_changed = Signal()
    rails = Property(QObject, rails, set_rails, notify=rails_changed)

    def settings(self):
        return self._settings

    def set_settings(self, value):
        self._settings = value
        self.settings_changed.emit()

    settings_changed = Signal()
    settings = Property(str, settings, set_settings, notify=settings_changed)
