# This Python file uses the following encoding: utf-8

from PySide6.QtCore import QObject
from PySide6.QtQml import QQmlApplicationEngine

from devices import Devices
#from rails import Rails
from network import Network
#from connector import Connector
from project_storage import ProjectStorage

class AppContext:
    def __init__(self, engine: QQmlApplicationEngine):
        self.context = engine.rootContext()

        projectStorage = ProjectStorage()
        devices = Devices()
        network = Network()

        self.setContextProperty("projectStorage", projectStorage)
        self.setContextProperty("project", projectStorage.currentProject)
        self.setContextProperty("devices", devices)
        self.setContextProperty("network", network)
        self.setContextProperty("connectorRegister", projectStorage.currentProject.connectorRegister)
        self.setContextProperty("rails", projectStorage.currentProject.rails)

    def setContextProperty(self, name: str, object: QObject):
        self.context.setContextProperty(name, object)

