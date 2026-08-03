# This Python file uses the following encoding: utf-8

from dataclasses import dataclass
import re

import networkx as nx
from PySide6.QtCore import QObject, Slot


@dataclass(frozen=True)
class LegResult:
    """Shortest-path leg between two graph nodes (QObject-free)."""

    nodes: list[str]
    segments: list[str]
    length: float


class Planner(QObject):
    def __init__(self, rails, network, parent=None):
        super().__init__(parent)
        self._rails = rails
        self._network = network

    def updateRailsModel(self, rails):
        self._rails = rails

    def compute_leg(self, from_node: str, to_node: str) -> LegResult | None:
        """Shortest path between two marker (or graph) nodes.

        Uses undirected edge weights. Switch position is not applied yet — the path
        may include either switch branch. A2.2 will add required_switches.

        Same-node (when the node exists): trivial leg with that node, empty
        segments, and length 0. Unknown nodes, missing graph, or no path: None.
        """
        graph = self._network.graph()
        if graph is None or from_node not in graph or to_node not in graph:
            return None
        if from_node == to_node:
            return LegResult(nodes=[from_node], segments=[], length=0.0)
        try:
            nodes = nx.shortest_path(graph, from_node, to_node, weight="weight")
            length = nx.shortest_path_length(graph, from_node, to_node, weight="weight")
        except nx.NetworkXNoPath:
            return None
        segments = [
            f"{a}:{b}"
            for a, b in (sorted((nodes[i], nodes[i + 1])) for i in range(len(nodes) - 1))
        ]
        return LegResult(nodes=nodes, segments=segments, length=float(length))

    @Slot(str)
    def reserve(self, segment_id):
        self._network.reserve(segment_id)

    @Slot(str)
    def unreserve(self, segment_id):
        self._network.unreserve(segment_id)

    @Slot(str)  # TODO - debug function more or less
    def plan(self, paths):
        paths = paths.split(",")
        planned_paths = {}
        for path in paths:
            match = re.match(r"(\d+)(.*)", path)
            if match:
                rail_id = int(match.group(1))
                path_id = match.group(2)
                planned_paths[rail_id] = path_id

        for rail in self._rails.items():
            path = planned_paths.get(rail.id, "None")
            rail._path_indicators.set_path_id_active(path)
