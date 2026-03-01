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
        self._segments = {} # lookup table

    def updateRailsModel(self, rails):
        self._rails = rails

    def segments(self):
        return self._segments

    @Slot()
    def generate(self):
        self._segments = {}
        self._graph = self._generator.generate(self._rails.items(), True)

        edges = self._graph.edges(data=True)

        for edge in edges:
            a, b = sorted(edge[0:2])
            id = f"{a}:{b}"
            self._segments[id] = edge

    def graph(self):
        return self._graph
