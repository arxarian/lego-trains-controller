# This Python file uses the following encoding: utf-8

from pathlib import Path

from PySide6.QtCore import QObject, Signal, Property

from rail import Rail
from rails import Rails
from settings import Settings
from connectorregister import ConnectorRegister

class Project(QObject):
    def __init__(self, name: str="", data: dict=None, parent=None):
        super().__init__(parent)
        self._named = False
        self._connectorRegister = ConnectorRegister(self)
        self._rails = Rails(self._connectorRegister, self)
        self._settings = Settings(parent=self)

        if data:
            self._rails.load_data([Rail.load_data(d, self._rails) for d in data.get("rails", [])])
            self._settings.deleteLater()
            self._settings = Settings.load_data(data.get("settings", {}), self)

        self.set_name(name)

    def data(self) -> dict:
        return {
            "rails": self._rails.save_data(),
            "settings": self._settings.save_data()
        }

    def name(self):
        return self._name

    def set_name(self, value):
        self._name = value
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
    named = Property(bool, named, set_named, notify=named_changed)

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
    settings = Property(QObject, settings, set_settings, notify=settings_changed)
