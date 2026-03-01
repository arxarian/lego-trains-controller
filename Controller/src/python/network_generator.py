from __future__ import annotations

import networkx as nx

from python.items.rail import RailType

def createNodeName(id0, id1=None):
    if id1 is None:
        return str(id0)
    a, b = sorted((str(id0), str(id1)))
    return f"{a}-{b}"

class NetworkGenerator():

    def __init__(self) -> None:
        self.graph = None
        self.rails = None

    def hasEdge(self, from_node, to_node):
        return self.graph.has_edge(from_node, to_node)

    def addEdge(self, from_node, to_node, marker, weight, rail_id, at_switch=False):
        if self.hasEdge(from_node, to_node):
            return

        self.graph.add_edge(from_node, to_node, weight=weight, rail_id=rail_id)

        if marker and not self.graph.nodes[to_node].get("marker", True):
            print("inconsitency at node ", to_node)

        # only to_node should be a marker
        if marker:
            self.graph.nodes[to_node]["marker"] = marker or self.graph.nodes[to_node].get("marker", False)

        if at_switch and "-" in from_node:
            self.graph.nodes[from_node]["at_switch"] = True
        if at_switch and "-" in to_node:
            self.graph.nodes[to_node]["at_switch"] = True

    def createGraph(self):
        for rail in self.rails:
            activeConnectors = rail.connectors.activeCount()
            paths = rail._paths
            at_switch = rail.type in (RailType.SwitchLeft, RailType.SwitchRight)

            # skip not connected
            if activeConnectors == 0:
                print("Network: Skipping not connected rail")
                continue

            for from_connector in rail.connectors._items:
                from_name = from_connector.name
                path = next(path for path in paths if path["from"] == from_name)
                path_id = path["path_id"]
                to_connector = rail.connectors.getByName(path["to"])

                both_connected = from_connector.connected() and to_connector.connected()
                either_connected = from_connector.connected() or to_connector.connected()

                if rail.markers.activeCount(path_id) == 0:
                    if both_connected:
                        from_node = createNodeName(rail.id, from_connector.connectedRailId)
                        to_node = createNodeName(rail.id, to_connector.connectedRailId)
                        self.addEdge(from_node, to_node, marker=False, weight=path["length"],
                            rail_id=rail.id, at_switch=at_switch)
                    elif either_connected:
                        from_node = createNodeName(f"{rail.id}{path_id}")
                        to_node = createNodeName(rail.id, rail.connectors.getFirstConnected().connectedRailId)
                        self.addEdge(from_node, to_node, marker=False, weight=path["length"],
                            rail_id=rail.id, at_switch=at_switch)
                else:
                    node = None
                    lastNode = None
                    lastDistance = 0
                    dir = from_connector.dir == "forward" # forward vs reverse

                    if both_connected:
                        node = createNodeName(rail.id, from_connector.connectedRailId)
                        lastNode = createNodeName(rail.id, to_connector.connectedRailId)
                    elif either_connected:
                        node = createNodeName(f"{rail.id}{path_id}")
                        lastNode = createNodeName(rail.id, rail.connectors.getFirstConnected().connectedRailId)
                        if dir is True: # swap when going forward
                            node, lastNode = lastNode, node

                    markers = rail.markers._items if dir else reversed(rail.markers._items)
                    visible_markers = (m for m in markers if m.visible and m.path_id in (None, "", path_id))

                    for marker in visible_markers:
                        to_node = f"{rail.id}{path_id}{marker.distance}"
                        self.addEdge(node, to_node, marker=True, weight=marker.distance - lastDistance,
                            rail_id=rail.id, at_switch=at_switch)
                        node = to_node
                        lastDistance = marker.distance

                    self.addEdge(node, lastNode, marker=False, weight=path["length"] - lastDistance,
                        rail_id=rail.id, at_switch=at_switch)

    def _is_important_node(self, node):
        """Node is important if it's a marker (for localization) or at a switch (path splitting)."""
        data = self.graph.nodes[node]
        return data.get("marker") or data.get("at_switch")

    def simplify_graph(self):
        def processArrays(arr1, arr2):
            def convertToArray(arr):
                if isinstance(arr, int):
                    return [arr]
                else:
                    return arr

            r = []
            r.extend(convertToArray(arr1))
            r.extend(convertToArray(arr2))
            #return sorted(set(r))
            return set(r)

        """
        Keep only important nodes (markers and switch-adjacent) and merge chains of
        non-important nodes between them. Uses NetworkX' degree / neighbors API
        instead of custom traversal logic.
        """
        G = self.graph
        important = {n for n in G if self._is_important_node(n)}
        if not important:
            return

        # Work on a copy so we don't mutate the original while iterating.
        H = G.copy()

        # For every non-important node with degree 2, merge its two incident edges
        # into a single edge between its neighbors, summing the weights.
        for node in list(H.nodes()):
            if node in important:
                continue

            deg = H.degree(node)
            if deg == 2:
                u, v = list(H.neighbors(node))
                w1 = H.edges[node, u].get("weight", 1)
                w2 = H.edges[node, v].get("weight", 1)
                rail_id1 = H.edges[node, u].get("rail_id", -1)
                rail_id2 = H.edges[node, v].get("rail_id", -1)

                new_w = w1 + w2
                ids = processArrays(rail_id1, rail_id2)

                if H.has_edge(u, v):
                    # Keep the shorter merged edge if there are multiple paths.
                    existing_w = H.edges[u, v].get("weight", float("inf"))
                    if new_w < existing_w:
                        H.edges[u, v]["weight"] = new_w
                else:
                    H.add_edge(u, v, weight=new_w, rail_id=ids)

            # In all cases, drop the non-important node itself (degree 0/1/2/...).
            H.remove_node(node)

        # Finally, keep only the important nodes and edges between them.
        self.graph = H.subgraph(important).copy()

    def generate(self, railsList, simplify=True):# -> nx.Graph:
        print("Network: Generating...")

        self.graph = nx.Graph()
        self.rails = railsList

        self.createGraph()
        if simplify:
            self.simplify_graph()

        #nx.nx_pydot.write_dot(self.graph, "src/out_graph.dot")

        print("Network: Done")
        return self.graph
