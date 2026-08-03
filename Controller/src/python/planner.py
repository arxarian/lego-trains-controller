# This Python file uses the following encoding: utf-8

from dataclasses import dataclass
import re

import networkx as nx
from PySide6.QtCore import QObject, Slot


@dataclass(frozen=True)
class RequiredSwitch:
    """Switch rail position required for a planned leg (rail_id → path_id A|B)."""

    rail_id: int
    path_id: str


@dataclass(frozen=True)
class LegResult:
    """Shortest-path leg between two graph nodes (QObject-free)."""

    nodes: list[str]
    segments: list[str]
    length: float
    required_switches: tuple[RequiredSwitch, ...] = ()


def collect_required_switches(rails, graph, nodes: list[str]) -> tuple[RequiredSwitch, ...] | None:
    """Derive required switch positions from path segment_data (not live switch state).

    Returns None if the same switch rail appears with conflicting path_ids.
    Non-switch rails are ignored. Order is first appearance along the path.
    """
    if graph is None or not nodes:
        return ()

    ordered: dict[int, str] = {}
    for i in range(len(nodes) - 1):
        a, b = nodes[i], nodes[i + 1]
        edge_data = graph.get_edge_data(a, b) or {}
        for rail_data in edge_data.get("segment_data", []):
            rail_id = int(rail_data["rail_id"])
            path_id = rail_data["path_id"]
            rail = rails.findRailData(rail_id)
            if rail is None or not rail.is_switch():
                continue
            if rail_id in ordered and ordered[rail_id] != path_id:
                return None
            if rail_id not in ordered:
                ordered[rail_id] = path_id

    return tuple(RequiredSwitch(rail_id=rid, path_id=pid) for rid, pid in ordered.items())


class Planner(QObject):
    def __init__(self, rails, network, parent=None):
        super().__init__(parent)
        self._rails = rails
        self._network = network

    def updateRailsModel(self, rails):
        self._rails = rails

    def compute_leg(self, from_node: str, to_node: str) -> LegResult | None:
        """Shortest path between two marker (or graph) nodes.

        Uses undirected edge weights. Switch position is not applied during search —
        either branch may appear. required_switches lists SwitchLeft/SwitchRight
        path_ids from the chosen path's segment_data (not live rail.switch_position).

        Same-node (when the node exists): trivial leg with that node, empty
        segments, length 0, and no required switches. Unknown nodes, missing
        graph, no path, or conflicting switch path_ids on one leg: None.
        """
        graph = self._network.graph()
        if graph is None or from_node not in graph or to_node not in graph:
            return None
        if from_node == to_node:
            return LegResult(nodes=[from_node], segments=[], length=0.0, required_switches=())
        try:
            nodes = nx.shortest_path(graph, from_node, to_node, weight="weight")
            length = nx.shortest_path_length(graph, from_node, to_node, weight="weight")
        except nx.NetworkXNoPath:
            return None
        segments = [
            f"{a}:{b}"
            for a, b in (sorted((nodes[i], nodes[i + 1])) for i in range(len(nodes) - 1))
        ]
        required = collect_required_switches(self._rails, graph, nodes)
        if required is None:
            return None
        return LegResult(
            nodes=nodes,
            segments=segments,
            length=float(length),
            required_switches=required,
        )

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
