# This Python file uses the following encoding: utf-8
from __future__ import annotations

from PySide6.QtCore import QObject, Slot, Property, Signal
from PySide6.QtGui import QColor
from python.items.rail import Rail
from python.network_generator import NetworkGenerator

class NetworkManager(QObject):
    def __init__(self, rails,  parent = None):
        super().__init__(parent)
        self._generator = NetworkGenerator()
        self._rails = rails
        self._graph = None
        self._nodeMarkerMap = {}
        self._segments = {} # lookup table
        self._owners = {}  # segment_id -> owner_id; missing key = free
        self._color_map = {} # color hex -> node_id
        self._has_graph = False
        self._marker_warnings = []

    def updateRailsModel(self, rails):
        self._rails = rails

    def graph(self):
        return self._graph

    def segments(self):
        return self._segments

    def owner_of(self, segment_id) -> str | None:
        return self._owners.get(segment_id)

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

    def try_reserve_segment(self, segment_id, owner) -> bool:
        if not segment_id or not owner:
            return False
        if segment_id not in self._segments:
            print(f"segment {segment_id} not found")
            return False

        current = self._owners.get(segment_id)
        if current is not None and current != owner:
            return False
        if current == owner:
            return True

        if not self.reserve(segment_id):
            return False
        self._owners[segment_id] = owner
        return True

    def release_segment(self, segment_id, owner) -> bool:
        if not segment_id or not owner:
            return False
        if self._owners.get(segment_id) != owner:
            return False

        del self._owners[segment_id]
        return self.unreserve(segment_id)

    def release_all_for(self, owner) -> None:
        if not owner:
            return
        for segment_id in [sid for sid, o in self._owners.items() if o == owner]:
            self.release_segment(segment_id, owner)
        self._unlock_switches_for(owner)

    def _required_switches_for_segments(self, segment_ids) -> list[tuple[Rail, str]] | None:
        """Switch rails and path_ids required by segment_data, or None on path_id conflict.

        Non-Rail / non-switch entries are ignored (keeps MagicMock rails in unit tests inert).
        """
        ordered: dict[int, tuple[Rail, str]] = {}
        for segment_id in segment_ids:
            segment = self._segments.get(segment_id)
            if segment is None:
                continue
            for rail_data in segment[2].get("segment_data", []):
                rail = self._rails.findRailData(rail_data["rail_id"])
                if not isinstance(rail, Rail) or not rail.is_switch():
                    continue
                path_id = rail_data["path_id"]
                if rail.id in ordered and ordered[rail.id][1] != path_id:
                    return None
                if rail.id not in ordered:
                    ordered[rail.id] = (rail, path_id)
        return list(ordered.values())

    def required_switches_for_segments(self, segment_ids) -> list[tuple[Rail, str]]:
        """Switch rails required by the leg, or empty if none / path conflict."""
        required = self._required_switches_for_segments(segment_ids)
        return required if required else []

    def _unlock_switches_for(self, owner) -> None:
        for rail in self._rails.items():
            if isinstance(rail, Rail) and rail.is_switch():
                rail.unlock_for(owner)

    def _unlock_all_switches(self) -> None:
        for rail in self._rails.items():
            if isinstance(rail, Rail) and rail.is_switch():
                rail.unlock()

    def _apply_switch_locks(self, owner, required: list[tuple[Rail, str]]) -> None:
        for rail, path_id in required:
            rail.set_switch_position(path_id)
            rail.lock_for(owner)

    def try_reserve_leg(self, owner, segment_ids) -> bool:
        """Atomically reserve every segment of a planned leg for owner.

        Auto executor (B1) entry point: call before departure with
        LegResult.segments. Returns True if all segments are free or already
        owned by owner (then owns all). Sets and locks required switch rails.
        Returns False on conflict, unknown segment, switch path conflict, or
        a required switch locked by another owner — ownership is unchanged (Hold).
        Empty leg succeeds.
        """
        if not owner:
            return False
        ids = list(segment_ids) if segment_ids else []
        if not ids:
            return True

        for segment_id in ids:
            if segment_id not in self._segments:
                return False
            current = self._owners.get(segment_id)
            if current is not None and current != owner:
                return False

        required = self._required_switches_for_segments(ids)
        if required is None:
            return False
        for rail, _path_id in required:
            locked_by = rail.locked_by
            if locked_by and locked_by != owner:
                return False

        newly_taken = []
        for segment_id in ids:
            if self._owners.get(segment_id) == owner:
                continue
            if not self.try_reserve_segment(segment_id, owner):
                for taken in newly_taken:
                    self.release_segment(taken, owner)
                return False
            newly_taken.append(segment_id)

        self._apply_switch_locks(owner, required)
        return True

    def release_leg(self, owner, segment_ids) -> bool:
        """Release listed segments owned by owner (arrival / cancel cleanup).

        Free segments are skipped. Segments owned by another party are left
        alone and cause False, but this owner's segments in the list are still
        released (best-effort). Unlocks switches locked by this owner. Empty
        list succeeds. Use release_all_for for pause/manual full cleanup.
        """
        if not owner:
            return False
        ids = list(segment_ids) if segment_ids else []
        ok = True
        for segment_id in ids:
            current = self._owners.get(segment_id)
            if current is None:
                continue
            if current != owner:
                ok = False
                continue
            if not self.release_segment(segment_id, owner):
                ok = False
        self._unlock_switches_for(owner)
        return ok

    def reserve_segments(self, segment_ids) -> bool:
        ok = True
        for segment_id in segment_ids or []:
            if not self.reserve(segment_id):
                ok = False
        return ok

    def unreserve_segments(self, segment_ids) -> bool:
        ok = True
        for segment_id in segment_ids or []:
            if not self.unreserve(segment_id):
                ok = False
        return ok

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
        self.marker_node_ids_changed.emit()

    def marker_node_ids(self):
        return sorted(self._color_map.values())

    marker_node_ids_changed = Signal()
    markerNodeIds = Property("QStringList", marker_node_ids, notify=marker_node_ids_changed)

    def find_node_marker(self, node_id: str):
        return self._nodeMarkerMap.get(node_id)

    @Slot(str, result=QColor)
    def color_for_node(self, node_id: str) -> QColor:
        marker = self.find_node_marker(node_id)
        if marker is None or marker.color is None:
            return QColor()
        return marker.color

    @Slot(int, str, int, result=str)
    def node_id_for_marker(self, rail_id: int, path_id: str, distance: int) -> str:
        """Return the unique graph node id for a placed marker, or empty if unknown/ambiguous."""
        node_ids = []
        for entry in self._collect_graph_markers():
            if entry["rail_id"] != rail_id or entry["distance"] != distance:
                continue
            if path_id not in (None, "", entry["path_id"]):
                continue
            if entry["node_id"] not in node_ids:
                node_ids.append(entry["node_id"])
        if len(node_ids) == 1:
            return node_ids[0]
        return ""

    def find_node_by_color(self, color_key: str):
        """color_key should be a lowercase hex string e.g. '#ff0000'"""
        return self._color_map.get(color_key)

    def _edge_matches_switch_state(self, node_id: str, neighbor: str) -> bool:
        """True if every switch rail on the edge matches its active path_id."""
        edge_data = self._graph.get_edge_data(node_id, neighbor) or {}
        for rail_data in edge_data.get("segment_data", []):
            rail = self._rails.findRailData(rail_data["rail_id"])
            if rail is None:
                return False
            if rail.is_switch() and rail.switch_position != rail_data["path_id"]:
                return False
        return True

    def _edge_involves_switch(self, node_id: str, neighbor: str) -> bool:
        """True if the edge includes any switch rail in segment_data."""
        edge_data = self._graph.get_edge_data(node_id, neighbor) or {}
        for rail_data in edge_data.get("segment_data", []):
            rail = self._rails.findRailData(rail_data["rail_id"])
            if rail is not None and rail.is_switch():
                return True
        return False

    def _resolve_exclude_neighbor(self, at_node: str, from_node: str | None) -> str | None:
        """Map a previous marker/node to the graph neighbor used to enter at_node.

        If resolving would exclude the only neighbor (dead-end marker), return
        None so the sole hop remains available (caller may reverse via that edge).
        """
        if from_node is None or self._graph is None:
            return None
        if not self._graph.has_node(at_node) or not self._graph.has_node(from_node):
            return None

        neighbors = list(self._graph.neighbors(at_node))
        if self._graph.has_edge(at_node, from_node):
            resolved = from_node
        else:
            # BFS from from_node to at_node; predecessor of at_node is the entry.
            prev = {from_node: None}
            queue = [from_node]
            resolved = None
            while queue:
                cur = queue.pop(0)
                for n in self._graph.neighbors(cur):
                    if n in prev:
                        continue
                    prev[n] = cur
                    if n == at_node:
                        resolved = prev[at_node]
                        queue.clear()
                        break
                    queue.append(n)

        if resolved is None:
            return None
        # Dead-end: excluding the only neighbor traps the walk; leave exclude empty.
        if len([n for n in neighbors if n != resolved]) == 0:
            return None
        return resolved

    def is_dead_end(self, node_id) -> bool:
        """True if node_id exists and has exactly one graph neighbor."""
        if self._graph is None or not node_id or node_id not in self._graph:
            return False
        return self._graph.degree(node_id) == 1

    def is_reverse_depart(self, current_node, previous_node, first_hop) -> bool:
        """True if first_hop goes back along arrival and current is not a dead-end.

        Uses the same entry-edge resolution as exclude_node. Dead-ends return
        False so the executor may reverse. Unknown/missing previous is not reverse.
        """
        if not current_node or not first_hop:
            return False
        if self.is_dead_end(current_node):
            return False
        entry = self._resolve_exclude_neighbor(current_node, previous_node)
        if entry is None:
            return False
        return first_hop == entry

    def _select_next_node(self, node_id: str, exclude_node: str = None) -> str | None:
        """Pick the next graph neighbor from node_id.

        Trailing into a switch (exclude is a branch edge): continue via stem only,
        never across the frog onto another branch.
        Facing from the stem (multiple branch candidates): use switch_position.
        A single forward hop is always allowed.
        """
        neighbors = list(self._graph.neighbors(node_id))
        candidates = [n for n in neighbors if n != exclude_node]
        if not candidates:
            print(f"Network: No forward neighbor from {node_id} (excluding {exclude_node})")
            return None

        # Trailing: entered via a switch branch — drop other switch-branch exits.
        if exclude_node is not None and self._edge_involves_switch(node_id, exclude_node):
            non_branch = [n for n in candidates if not self._edge_involves_switch(node_id, n)]

            if non_branch:
                candidates = non_branch

        if len(candidates) == 1:
            return candidates[0]

        compatible = [n for n in candidates if self._edge_matches_switch_state(node_id, n)]
        if len(compatible) == 1:
            return compatible[0]
        if not compatible:
            print(
                f"Network: No switch-compatible neighbor from {node_id} "
                f"(excluding {exclude_node}); candidates={candidates}"
            )
            return None
        # Switch state did not uniquely select (e.g. no switch on edges,
        # or first localization with empty exclude_node).
        print(
            f"Network: Multiple switch-compatible neighbors from {node_id} "
            f"(excluding {exclude_node}), picking first: {compatible}"
        )
        return compatible[0]

    def find_segment_by_entry_node(self, node_id: str, exclude_node: str = None) -> str:
        """Return the segment ID the train enters after arriving at node_id.
        exclude_node is the node the train came from (to avoid going backward)."""
        exclude = self._resolve_exclude_neighbor(node_id, exclude_node)
        next_node = self._select_next_node(node_id, exclude)
        if next_node is None:
            return None
        a, b = sorted([node_id, next_node])
        return f"{a}:{b}"

    def find_segments_to_next_marker(self, from_node: str, exclude_node: str = None) -> list[str]:
        """Segment ids from from_node through switch nodes until next marker."""
        segments, _ = self.walk_to_next_marker(from_node, exclude_node)
        return segments

    def find_next_marker_node(self, from_node: str, exclude_node: str = None) -> str | None:
        """Walk switch-aware edges from from_node until the next marker node."""
        _, next_marker = self.walk_to_next_marker(from_node, exclude_node)
        return next_marker

    def walk_to_next_marker(self, from_node: str, exclude_node: str = None) -> tuple[list[str], str | None]:
        """Return (segment_ids, next_marker_node) or ([], None) if stuck."""
        if self._graph is None or from_node is None:
            return [], None
        marker_nodes = set(self._color_map.values())
        prev = self._resolve_exclude_neighbor(from_node, exclude_node)
        node = from_node
        seen = {from_node}
        segment_ids = []
        while True:
            next_node = self._select_next_node(node, prev)
            if next_node is None:
                return [], None
            a, b = sorted([node, next_node])
            segment_ids.append(f"{a}:{b}")
            if next_node in marker_nodes:
                return segment_ids, next_node
            if next_node in seen:
                return [], None
            seen.add(next_node)
            prev = node
            node = next_node

    @Slot()
    def generate(self):
        self._segments = {}
        self._owners = {}
        self._unlock_all_switches()
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
    markerWarnings = Property("QStringList", marker_warnings, set_marker_warnings, notify=marker_warnings_changed)
