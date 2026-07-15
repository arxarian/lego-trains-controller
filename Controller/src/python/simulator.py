from __future__ import annotations

import asyncio
from PySide6.QtCore import QObject, Property, Signal, Slot
from PySide6.QtGui import QColor

from python.items.fake_device import FakeDevice, TRANSPARENT_COLOR

class Simulator(QObject):

    def __init__(self, network, trains, parent=None):
        super().__init__(parent)
        self._network = network
        self._trains = trains
        self._is_running = False
        self._fake_device = None
        self._train = None
        self._circuit = []
        self._run_task = None
        self._current_index = 0
        self._step_delay = 1.5
        self._pause_delay = 0.3

    def is_running(self):
        return self._is_running

    def set_is_running(self, value):
        self._is_running = value
        self.is_running_changed.emit()

    is_running_changed = Signal()
    is_running = Property(bool, is_running, set_is_running, notify=is_running_changed)

    def _build_circuit(self):
        """Walk the color map to build an ordered circuit."""
        color_map = self._network._color_map

        marker_nodes = set(color_map.values())
        if not marker_nodes:
            return []

        start = next(iter(marker_nodes))
        circuit = []
        visited = set()
        current = start

        while current not in visited:
            visited.add(current)
            color_hex = next((c for c, n in color_map.items() if n == current), None)
            if color_hex:
                circuit.append((current, color_hex))
            current = self._next_marker_neighbor(current, visited, marker_nodes)
            if current is None:
                break

        if circuit and start in marker_nodes:
            color_hex = next((c for c, n in color_map.items() if n == start), None)
            if color_hex and circuit[0][0] != start:
                circuit.append((start, color_hex))

        print(f"Simulator: circuit has {len(circuit)} stops: {[c[0] for c in circuit]}")
        return circuit

    def _next_marker_neighbor(self, node_id, visited, marker_nodes):
        """Find the next unvisited marker node reachable from node_id, skipping intermediates."""
        graph = self._network._graph
        queue = list(graph.neighbors(node_id))
        seen = {node_id}
        while queue:
            candidate = queue.pop(0)
            if candidate in seen:
                continue
            seen.add(candidate)
            if candidate in marker_nodes and candidate not in visited:
                return candidate
            for n in graph.neighbors(candidate):
                if n not in seen:
                    queue.append(n)
        return None

    @Slot()
    def onSpeedChanged(self):
        # change simulation speed
        if self._fake_device.speed == 0:
            self.pause_simulation()
            return

        if self._is_running == False:
            self.unpause_simulation()

        # 25 = 1.6
        # 50 = 0.8
        # 100 = 0.4
        self._step_delay = 40 / self._fake_device.speed
        print("speed changed", self._fake_device.speed, "simulation speed", self._step_delay)


    @Slot()
    def start(self):
        if self._is_running:
            return

        self._circuit = self._build_circuit()
        if not self._circuit:
            print("Simulator: empty circuit, cannot start")
            return

        self._current_index = 0
        self._fake_device = FakeDevice(name="Simulator", parent=self)
        self._fake_device.set_speed(30)
        self._train = self._trains.add_train(self._fake_device)
        self._fake_device.disconnected.connect(self.on_fake_device_disconnected)
        self._fake_device.speed_changed.connect(self.onSpeedChanged)

        self.set_is_running(True)
        self._run_task = asyncio.ensure_future(self.run_loop())

    @Slot()
    def stop(self):
        if not self._is_running:
            return

        self.set_is_running(False)

        if self._run_task:
            self._run_task.cancel()
            self._run_task = None

        if self._train and self._train._current_segment_id:
            self._network.unreserve(self._train._current_segment_id)

        if self._fake_device:
            self._trains.remove_by_device(self._fake_device)
            self._fake_device = None
            self._train = None

    def on_fake_device_disconnected(self, device):
        if self._is_running:
            self.stop()

    def pause_simulation(self):
        self._is_running = False

    def unpause_simulation(self):
        self._is_running = True
        self._run_task = asyncio.ensure_future(self.run_loop())

    async def run_loop(self):

        while self._is_running:
            _, color_hex = self._circuit[self._current_index]

            color = QColor(color_hex)
            self._fake_device.set_color(color)
            await asyncio.sleep(self._pause_delay)

            if not self._is_running:
                return

            self._fake_device.set_color(TRANSPARENT_COLOR)
            await asyncio.sleep(self._step_delay)

            if not self._is_running:
                return

            self._current_index = (self._current_index + 1) % len(self._circuit)
