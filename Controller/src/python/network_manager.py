# This Python file uses the following encoding: utf-8
from __future__ import annotations

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

    def graph(self):
        return self._graph

    def segments(self):
        return self._segments

    def reserve(self, segment_id) -> bool:
        if segment_id not in self._segments:
            print(f"segment {segment_id} not found")
            return False

        segment = self._segments[segment_id]

        for rail_data in segment[2]["segment_data"]:
            rail = self._rails.findRailData(rail_data["rail_id"])
            rail.reserve_segment(rail_data["path_id"], rail_data["from"], rail_data["to"])

        return True

    @Slot()
    def generate(self):
        self._segments = {}
        self._graph = self._generator.generate(self._rails.items(), True)

        edges = self._graph.edges(data=True)

        for edge in edges:
            a, b = sorted(edge[0:2])
            id = f"{a}:{b}"
            self._segments[id] = edge
