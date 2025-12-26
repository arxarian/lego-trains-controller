from __future__ import annotations

import webcolors

from PySide6.QtCore import QObject, Slot
from PySide6.QtGui import QColor
from connector import State

MARKERS_MAX_DIST = 1

class Node:
    def __init__(self, rail_id, connector_name):
        self.id = f"{rail_id}:{connector_name}"
        self.rail_id = rail_id
        self.connector = connector_name
        self.markers = []  # optional markers along the rail between connectors

class ClusteredMarker:
    def __init__(self, marker: QObject):
        self.startPosition = marker.index
        self.endPosition = marker.index
        self.colors = [marker.color]

    def addMarker(self, marker: QObject):
        self.endPosition = marker.index
        self.colors.append(marker.color)

    def prettyPrint(self):
        for color in self.colors:
            print(webcolors.hex_to_name(color.name()), end=" ")
        print()

class Network(QObject):

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.graph = {}
        self.clusteredMarkers = []

    def clusterMarkers(self, rails):
        distance = 0

        for rail in rails._items:   # TODO - last and first rail
            markers = rail._markers._items

            for marker in markers:
                if marker.visible:
                    if distance > MARKERS_MAX_DIST:
                        self.clusteredMarkers.append(ClusteredMarker(marker))
                        distance = -1
                    else:
                        self.clusteredMarkers[-1].addMarker(marker)
                        distance = -1

                distance = distance + 1

        for markers in self.clusteredMarkers:
            markers.prettyPrint()


    @Slot(QObject)
    def generate(self, rails):
        print("Network: generating...")

        graph = {}
        self.clusterMarkers(rails)
        self.graph = graph

        print("Done")

