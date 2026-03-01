# This Python file uses the following encoding: utf-8
from __future__ import annotations

#import networkx as nx

from PySide6.QtCore import QObject, Slot
from python.network_generator import NetworkGenerator

class NetworkManager(QObject):
    def __init__(self, rails,  parent = None):
        super().__init__(parent)
        self._generator = NetworkGenerator()
        self._rails = rails
        self._graph = None

    def updateRailsModel(self, rails):
        self._rails = rails

    def segmments(self):
        if self._graph is None:
            return []

        #

    @Slot()
    def generate(self):
        self._graph = self._generator.generate(self._rails.items(), True)

    def graph(self):
        return self._graph
