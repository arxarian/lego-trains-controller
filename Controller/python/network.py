from __future__ import annotations

import networkx as nx

from PySide6.QtCore import QObject, Slot

def createNodeName(id0, id1=None):
    if id1 is None:
        return str(id0)
    a, b = sorted((str(id0), str(id1)))
    return f"{a}-{b}"

class Network(QObject):

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.graph = None
        self.rails = None

    def addEdge(self, node_0, node_1, marker, weight):
        self.graph.add_edge(node_0, node_1, weight=weight)
        self.graph.add_node(node_0, marker=marker)

    def createGraph(self):
        for rail in self.rails._items:
            activeConnectors = rail.connectors.activeCount()
            paths = rail._paths

            # skip not connected
            if activeConnectors == 0:
                print("Network: Skipping not connected rail")
                continue

            for from_connector in rail.connectors._items:
                from_name = from_connector.name
                path = next(path for path in paths if path["from"] == from_name)
                to_connector = rail.connectors.getByName(path["to"])

                both_connected = from_connector.connected() and to_connector.connected()
                either_connected = from_connector.connected() or to_connector.connected()

                if rail.markers.activeCount() == 0:
                    if both_connected:
                        node_0 = createNodeName(rail.id, from_connector.connectedRailId)
                        node_1 = createNodeName(rail.id, to_connector.connectedRailId)
                        self.addEdge(node_0, node_1, False, weight=path["length"])
                    elif either_connected:
                        node_0 = createNodeName(f"{rail.id}{path['path']}")
                        node_1 = createNodeName(rail.id, rail.connectors.getFirstConnected().connectedRailId)
                        self.addEdge(node_0, node_1, True, 16) # TODO - length
                else:
                    node = None
                    lastNode = None
                    lastDistance = 0

                    if both_connected:
                        node = createNodeName(rail.id, from_connector.connectedRailId)
                        lastNode = createNodeName(rail.id, to_connector.connectedRailId)
                    elif either_connected:
                        node = createNodeName(f"{rail.id}{path['path']}")
                        lastNode = createNodeName(rail.id, rail.connectors.getFirstConnected().connectedRailId)

                    markers = rail.markers._items if from_connector.dir == "start" else reversed(rail.markers._items)
                    visible_markers = (m for m in markers if m.visible)

                    for marker in visible_markers:
                        to_node = f"{rail.id}D{marker.distance}"
                        self.addEdge(node, to_node, True, marker.distance)
                        node = to_node
                        lastDistance = marker.distance

                    self.addEdge(node, lastNode, True, weight=path["length"] - lastDistance)

    @Slot(QObject)
    def generate(self, rails):
        print("Network: Generating...")

        self.graph = nx.Graph()
        self.rails = rails

        self.createGraph()

        nx.nx_pydot.write_dot(self.graph, "debug_graph.dot")

        print("Network: Done")

