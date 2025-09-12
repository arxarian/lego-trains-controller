# This Python file uses the following encoding: utf-8

from PySide6.QtCore import QObject
from PySide6.QtQml import QQmlApplicationEngine

from devices import Devices
from network import Network
from project_storage import ProjectStorage

class AppContext:
    def __init__(self, engine: QQmlApplicationEngine):
        self.context = engine.rootContext()

        self.projectStorage = ProjectStorage()
        self.devices = Devices()
        self.network = Network()

        self.setContextProperty("projectStorage", self.projectStorage)
        self.setContextProperty("project", self.projectStorage.currentProject)
        self.setContextProperty("devices", self.devices)
        self.setContextProperty("network", self.network)
        self.setContextProperty("connectorRegister", self.projectStorage.currentProject.connectorRegister)
        self.setContextProperty("rails", self.projectStorage.currentProject.rails)

    def setContextProperty(self, name: str, object: QObject):
        self.context.setContextProperty(name, object)

