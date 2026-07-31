from __future__ import annotations

import asyncio
from PySide6.QtCore import QObject, Property, Signal, Slot
from PySide6.QtGui import QColor

from python.items.train_device import TRANSPARENT_COLOR
from python.items.train_device_sim import TrainDeviceSim


class Simulator(QObject):

    def __init__(self, network, trains, parent=None):
        super().__init__(parent)
        self._network = network
        self._trains = trains
        self._is_running = False
        self._fake_device = None
        self._train = None
        self._run_task = None
        self._current_node_id = None
        self._previous_node_id = None
        self._marker_consumed = False
        self._step_delay = 1.5
        self._pause_delay = 0.3

    def is_running(self):
        return self._is_running

    def set_is_running(self, value):
        self._is_running = value
        self.is_running_changed.emit()

    is_running_changed = Signal()
    is_running = Property(bool, is_running, set_is_running, notify=is_running_changed)

    def _color_for_node(self, node_id):
        """Return hex color for a marker node, or None."""
        for color_hex, mapped in self._network._color_map.items():
            if mapped == node_id:
                return color_hex
        return None

    def _advance_to_next_marker(self) -> bool:
        """Move current/previous to the next switch-aware marker. Returns False if stuck."""
        next_node = self._network.find_next_marker_node(
            self._current_node_id, self._previous_node_id
        )
        if next_node is None:
            # Dead end: reverse by allowing the back-neighbor.
            next_node = self._network.find_next_marker_node(
                self._current_node_id, None
            )
        if next_node is None:
            print(
                f"Simulator: no next marker from {self._current_node_id} "
                f"(prev={self._previous_node_id})"
            )
            return False
        self._previous_node_id = self._current_node_id
        self._current_node_id = next_node
        return True

    @Slot()
    def onSpeedChanged(self):
        if self._fake_device is None:
            return

        if self._fake_device.speed == 0:
            self.pause_simulation()
            return

        if self._run_task is None or self._run_task.done():
            self.unpause_simulation()

        # 25 = 1.6
        # 50 = 0.8
        # 100 = 0.4
        self._step_delay = 40 / self._fake_device.speed
        print("speed changed", self._fake_device.speed, "simulation speed", self._step_delay)

    def _cancel_run_task(self):
        if self._run_task and not self._run_task.done():
            self._run_task.cancel()
        self._run_task = None

    @Slot()
    def start(self):
        if self._is_running:
            return

        color_map = self._network._color_map
        if not color_map:
            print("Simulator: empty color map, cannot start")
            return

        self._current_node_id = next(iter(color_map.values()))
        self._previous_node_id = None
        self._marker_consumed = False
        self._fake_device = TrainDeviceSim(name="Simulator", parent=self)
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
        self._cancel_run_task()
        self._marker_consumed = False
        self._current_node_id = None
        self._previous_node_id = None

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
        """Stop advancing; keep reserved segment and last known position."""
        self._cancel_run_task()
        if self._fake_device:
            self._fake_device.set_color(TRANSPARENT_COLOR)

    def unpause_simulation(self):
        if not self._is_running:
            return
        if self._run_task and not self._run_task.done():
            return

        # Already localized at current marker — continue from the next one.
        if self._marker_consumed and self._current_node_id:
            if not self._advance_to_next_marker():
                return
            self._marker_consumed = False

        self._run_task = asyncio.ensure_future(self.run_loop())

    async def run_loop(self):
        try:
            while self._is_running:
                color_hex = self._color_for_node(self._current_node_id)
                if color_hex is None:
                    print(
                        f"Simulator: no color for node {self._current_node_id}"
                    )
                    return

                color = QColor(color_hex)
                self._fake_device.set_color(color)
                self._marker_consumed = True
                await asyncio.sleep(self._pause_delay)

                if not self._is_running:
                    return

                self._fake_device.set_color(TRANSPARENT_COLOR)
                await asyncio.sleep(self._step_delay)

                if not self._is_running:
                    return

                if not self._advance_to_next_marker():
                    return
                self._marker_consumed = False
        except asyncio.CancelledError:
            return
