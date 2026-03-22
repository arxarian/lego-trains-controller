# This Python file uses the following encoding: utf-8

from PySide6.QtCore import QObject, Slot
from PySide6.QtQml import QQmlApplicationEngine

from python.models.devices import Devices
from python.network_manager import NetworkManager
from python.models.project_storage import ProjectStorage
from python.models.marker_types import MarkerTypes
from python.models.rail_types import RailTypes
from python.planner import Planner
from python.models.path_indicators_filter import PathIndicatorsFilter
from python.models.trains import Trains
from python.simulator import Simulator

class AppContext:
    def __init__(self, engine: QQmlApplicationEngine):
        self.context = engine.rootContext()

        self.projectStorage = ProjectStorage()
        self.devices = Devices()
        self.markerTypes = MarkerTypes()
        self.railTypes = RailTypes()
        self.network = NetworkManager(self.projectStorage.currentProject.rails)
        self.planner = Planner(self.projectStorage.currentProject.rails, self.network)
        self.trains = Trains(self.network, self.devices)
        self.simulator = Simulator(self.network, self.trains)

        self.projectStorage.currentProject_changed.connect(self.updateProjectProperties)
        self.updateProjectProperties()

        self.setContextProperty("projectStorage", self.projectStorage)
        self.setContextProperty("devices", self.devices)
        self.setContextProperty("network", self.network)
        self.setContextProperty("markerTypes", self.markerTypes)
        self.setContextProperty("railTypes", self.railTypes)
        self.setContextProperty("planner", self.planner)
        self.setContextProperty("trains", self.trains)
        self.setContextProperty("simulator", self.simulator)

    def setContextProperty(self, name: str, object: QObject):
        self.context.setContextProperty(name, object)

    @Slot()
    def updateProjectProperties(self):
            self.planner.updateRailsModel(self.projectStorage.currentProject.rails)
            self.network.updateRailsModel(self.projectStorage.currentProject.rails)
            self.setContextProperty("project", self.projectStorage.currentProject)
            self.setContextProperty("settings", self.projectStorage.currentProject.settings)
            self.setContextProperty("connectorRegister", self.projectStorage.currentProject.connectorRegister)
            self.setContextProperty("rails", self.projectStorage.currentProject.rails)

