from __future__ import annotations

import webcolors
import networkx as nx

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
        self.graph = None
        self.clusteredMarkers = []

    def createNodeName(self, id0, id1):
        return str(min(id0, id1)) + "-" + str(max(id0, id1))

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

        print("Clusters")
        for markers in self.clusteredMarkers:
            markers.prettyPrint()


    @Slot(QObject)
    def generate(self, rails):
        print("Network: Generating...")

        graph = nx.Graph()

        print("Start", rails._items[0].id)

        for rail in rails._items:
            #print(rail.toString())

            paths = rail._paths
            for from_connector in rail.connectors._items:
                if from_connector.connected():
                    from_name = from_connector.name
                    path = next(path for path in paths if path["from"] == from_name)
                    to_connector = rail.connectors.getByName(path["to"])

                    if to_connector.connected():
                        node_0 = self.createNodeName(rail.id, from_connector.connectedRailId)
                        node_1 = self.createNodeName(rail.id, to_connector.connectedRailId)

                        graph.add_edge(node_0, node_1, weight=path["length"])

        #edges = list(nx.dfs_edges(graph, source=rails._items[0].id))
        print("nodes", graph.nodes())
        print("edges", graph.edges())

        nx.nx_pydot.write_dot(graph, "debug_graph.dot")


        self.graph = graph

        print("Network: Done")

