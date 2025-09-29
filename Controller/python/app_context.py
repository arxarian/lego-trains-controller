# This Python file uses the following encoding: utf-8

from PySide6.QtCore import QObject, Slot
from PySide6.QtQml import QQmlApplicationEngine

from devices import Devices
from network import Network
from project_storage import ProjectStorage
from marker_types import MarkerTypes
from rail_types import RailTypes

class AppContext:
    def __init__(self, engine: QQmlApplicationEngine):
        self.context = engine.rootContext()

        self.projectStorage = ProjectStorage()
        self.devices = Devices()
        self.network = Network()
        self.markerTypes = MarkerTypes()
        self.railTypes = RailTypes()

        self.projectStorage.currentProject_changed.connect(self.updateProjectProperties)
        self.updateProjectProperties()

        self.setContextProperty("projectStorage", self.projectStorage)
        self.setContextProperty("devices", self.devices)
        self.setContextProperty("network", self.network)
        self.setContextProperty("markerTypes", self.markerTypes)
        self.setContextProperty("railTypes", self.railTypes)

    def setContextProperty(self, name: str, object: QObject):
        self.context.setContextProperty(name, object)

    @Slot()
    def updateProjectProperties(self):
            self.setContextProperty("project", self.projectStorage.currentProject)
            self.setContextProperty("settings", self.projectStorage.currentProject.settings)
            self.setContextProperty("connectorRegister", self.projectStorage.currentProject.connectorRegister)
            self.setContextProperty("rails", self.projectStorage.currentProject.rails)

