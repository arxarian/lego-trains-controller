from __future__ import annotations

import asyncio

from PySide6.QtCore import QObject, Property, Signal, Slot
from PySide6.QtGui import QColor

from python.items.fake_device import FakeDevice, TRANSPARENT_COLOR


class Simulator(QObject):

    def __init__(self, network, trains, interval_s=2.0, parent=None):
        super().__init__(parent)
        self._network = network
        self._trains = trains
        self._interval_s = interval_s
        self._is_running = False
        self._fake_device = None
        self._train = None
        self._circuit = []

    def _build_circuit(self) -> list[tuple[str, str]]:
        """Walk the graph through marker nodes only, building an ordered circuit.
        Returns a list of (node_id, color_hex) tuples in traversal order."""
        color_map = self._network._color_map
        if not color_map:
            return []

        node_to_color = {node: color for color, node in color_map.items()}
        marker_nodes = set(node_to_color.keys())

        start_node = next(iter(marker_nodes))
        circuit = []
        current = start_node
        prev = None

        while True:
            circuit.append((current, node_to_color[current]))

            # Find the next marker node neighbor (skip non-marker intermediates)
            next_marker = self._next_marker_neighbor(current, prev, marker_nodes)
            if next_marker is None or next_marker == start_node:
                break

            prev = current
            current = next_marker

        return circuit

    def _next_marker_neighbor(self, node: str, exclude: str, marker_nodes: set) -> str | None:
        """From node, follow graph edges to find the next marker node,
        skipping any non-marker intermediates (e.g. switch-adjacent nodes)."""
        visited = {node}
        if exclude:
            visited.add(exclude)

        frontier = [n for n in self._network._graph.neighbors(node) if n not in visited]

        while frontier:
            candidate = frontier.pop(0)
            if candidate in marker_nodes:
                return candidate
            visited.add(candidate)
            frontier.extend(n for n in self._network._graph.neighbors(candidate)
                            if n not in visited)
        return None

    @Slot()
    def start(self):
        if self._is_running:
            return

        if self._network._graph is None or not self._network._color_map:
            print("Simulator: network not generated yet — click 'Generate graph' first")
            return

        self._circuit = self._build_circuit()
        if not self._circuit:
            print("Simulator: could not build a circuit from the color map")
            return

        print(f"Simulator: circuit has {len(self._circuit)} stops: "
              f"{[node for node, _ in self._circuit]}")

        self._fake_device = FakeDevice(name="Simulator")
        self._fake_device.disconnected.connect(self._on_fake_device_disconnected)
        self._train = self._trains.add_train(self._fake_device)

        self.set_is_running(True)
        asyncio.create_task(self._run_loop())

    @Slot()
    def stop(self):
        if not self._is_running:
            return

        self.set_is_running(False)

        if self._train and self._train._current_segment_id:
            self._network.unreserve(self._train._current_segment_id)

        if self._fake_device:
            fd = self._fake_device
            self._fake_device = None
            self._train = None
            self._trains.remove_by_device(fd)

    def _on_fake_device_disconnected(self, _):
        """Called when the user clicks Disconnect/Shut Down on the simulated train panel."""
        if not self._is_running:
            return
        self.set_is_running(False)
        if self._train and self._train._current_segment_id:
            self._network.unreserve(self._train._current_segment_id)
        self._fake_device = None
        self._train = None

    async def _run_loop(self):
        idx = 0
        while self._is_running:
            node_id, color_hex = self._circuit[idx]
            self._fake_device.set_color(QColor(color_hex))
            await asyncio.sleep(self._interval_s)
            if not self._is_running:
                break
            self._fake_device.set_color(TRANSPARENT_COLOR)
            await asyncio.sleep(0.2)
            idx = (idx + 1) % len(self._circuit)

    def is_running(self):
        return self._is_running

    def set_is_running(self, value):
        self._is_running = value
        self.is_running_changed.emit()

    is_running_changed = Signal()
    is_running = Property(bool, is_running, set_is_running, notify=is_running_changed)
