# This Python file uses the following encoding: utf-8
from __future__ import annotations

from PySide6.QtCore import QObject, Slot, Property, Signal
from python.network_generator import NetworkGenerator

class NetworkManager(QObject):
    def __init__(self, rails,  parent = None):
        super().__init__(parent)
        self._generator = NetworkGenerator()
        self._rails = rails
        self._graph = None
        self._nodeMarkerMap = {}
        self._segments = {} # lookup table
        self._color_map = {} # color hex -> node_id
        self._has_graph = False
        self._marker_warnings = []

    def updateRailsModel(self, rails):
        self._rails = rails

    def graph(self):
        return self._graph

    def segments(self):
        return self._segments

    def _apply_to_segment(self, segment_id, fn) -> bool:
        if segment_id not in self._segments:
            print(f"segment {segment_id} not found")
            return False

        segment = self._segments[segment_id]
        for rail_data in segment[2]["segment_data"]:
            rail = self._rails.findRailData(rail_data["rail_id"])
            fn(rail, rail_data["path_id"], rail_data["from"], rail_data["to"])
        return True

    def reserve(self, segment_id) -> bool:
        if segment_id:
            return self._apply_to_segment(
                segment_id,
                lambda rail, path_id, from_d, to_d: rail.reserve_segment(path_id, from_d, to_d)
            )
        return False

    def unreserve(self, segment_id) -> bool:
        if segment_id:
            return self._apply_to_segment(
                segment_id,
                lambda rail, path_id, from_d, to_d: rail.unreserve_segment(path_id, from_d, to_d)
            )
        return False

    def _collect_graph_markers(self):
        """Return taken colored markers that exist as graph nodes."""
        results = []
        if self._graph is None:
            return results

        for rail in self._rails.items():
            for path in rail._paths:
                path_id = path["path_id"]
                for marker in rail.markers._items:
                    if marker.taken and marker.path_id in (None, "", path_id) and marker.color is not None:
                        node_id = f"{rail.id}{path_id}{marker.distance}"
                        if self._graph.has_node(node_id):
                            results.append({
                                "color_key": marker.color.name(),
                                "node_id": node_id,
                                "rail_id": rail.id,
                                "path_id": path_id,
                                "distance": marker.distance,
                            })
        return results

    def validate_markers(self) -> list[str]:
        """Detect duplicate colors among graph markers."""
        warnings = []
        markers = self._collect_graph_markers()

        by_color: dict[str, list[str]] = {}
        for entry in markers:
            nodes = by_color.setdefault(entry["color_key"], [])
            if entry["node_id"] not in nodes:
                nodes.append(entry["node_id"])

        for color_key, nodes in by_color.items():
            if len(nodes) > 1:
                warnings.append(
                    f"Duplicate marker color {color_key} at nodes: {', '.join(nodes)}"
                )

        return warnings

    def build_color_map(self):
        self._color_map = {}
        for entry in self._collect_graph_markers():
            color_key = entry["color_key"]
            node_id = entry["node_id"]
            if color_key in self._color_map:
                existing = self._color_map[color_key]
                if existing != node_id:
                    print(
                        f"Network: Color map collision for {color_key}: "
                        f"keeping {existing}, ignoring {node_id}"
                    )
                continue
            self._color_map[color_key] = node_id
        print(f"Network: Color map built with {len(self._color_map)} entries: {self._color_map}")

    def find_node_marker(self, node_id: str):
        return self._nodeMarkerMap.get(node_id)

    def find_node_by_color(self, color_key: str):
        """color_key should be a lowercase hex string e.g. '#ff0000'"""
        return self._color_map.get(color_key)

    def find_segment_by_entry_node(self, node_id: str, exclude_node: str = None) -> str:
        """Return the segment ID the train enters after arriving at node_id.
        exclude_node is the node the train came from (to avoid going backward)."""
        neighbors = list(self._graph.neighbors(node_id))
        candidates = [n for n in neighbors if n != exclude_node]
        if not candidates:
            print(f"Network: No forward neighbor from {node_id} (excluding {exclude_node})")
            return None
        if len(candidates) > 1:
            # TODO: use direction + switch state to pick the correct branch
            print(f"Network: Multiple forward neighbors from {node_id}, picking first: {candidates}")
        next_node = candidates[0]
        a, b = sorted([node_id, next_node])
        return f"{a}:{b}"

    @Slot()
    def generate(self):
        self._segments = {}
        self._graph, self._nodeMarkerMap = self._generator.generate(self._rails.items(), True)

        edges = self._graph.edges(data=True)

        for edge in edges:
            a, b = sorted(edge[0:2])
            id = f"{a}:{b}"
            self._segments[id] = edge

        self.build_color_map()
        self.set_marker_warnings(self.validate_markers())
        self.set_has_graph(True)

    def has_graph(self):
        return self._has_graph

    def set_has_graph(self, value):
        self._has_graph = value
        self.has_graph_changed.emit()

    has_graph_changed = Signal()
    has_graph = Property(bool, has_graph, set_has_graph, notify=has_graph_changed)

    def marker_warnings(self):
        return self._marker_warnings

    def set_marker_warnings(self, value):
        self._marker_warnings = list(value) if value else []
        self.marker_warnings_changed.emit()

    marker_warnings_changed = Signal()
    markerWarnings = Property(
        "QStringList", marker_warnings, set_marker_warnings, notify=marker_warnings_changed
    )
