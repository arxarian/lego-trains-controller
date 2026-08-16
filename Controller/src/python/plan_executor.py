# This Python file uses the following encoding: utf-8
from __future__ import annotations

import asyncio

from PySide6.QtCore import QObject, Property, Signal, Slot
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "TrainView"
QML_IMPORT_MAJOR_VERSION = 1

FALLBACK_SPEED = 40


class ExecutorState:
    IDLE = "Idle"
    WAITING_FOR_LOCALIZATION = "Waiting for localization"
    HOLD = "Hold"
    MOVING = "Moving"
    WAITING = "Waiting"
    PAUSED = "Paused"


@QmlElement
class PlanExecutor(QObject):
    """Loops a train's orders with whole-leg reservation and Hold on conflict."""

    def __init__(self, train, planner, network, parent=None, hold_retry_s=0.5):
        super().__init__(parent)
        self._train = train
        self._planner = planner
        self._network = network
        self._hold_retry_s = float(hold_retry_s)
        self._state = ExecutorState.PAUSED
        self._hold_reason = ""
        self._previous_node_id = ""
        self._current_leg = None
        self._cruise_speed = 0
        self._paused_while_waiting = False
        self._task = None
        self._train.device.speed_changed.connect(self._capture_cruise)

    def status(self):
        if self._state == ExecutorState.HOLD and self._hold_reason:
            return f"{ExecutorState.HOLD}: {self._hold_reason}"
        return self._state

    status_changed = Signal()
    status = Property(str, status, notify=status_changed)

    def state(self):
        return self._state

    def previous_node_id(self):
        return self._previous_node_id

    def set_previous_node_id(self, value):
        self._previous_node_id = value or ""

    def _set_state(self, value, reason=""):
        self._hold_reason = reason if value == ExecutorState.HOLD else ""
        if self._state != value or reason:
            self._state = value
            self.status_changed.emit()

    def _owner(self):
        return self._train.device.name

    def _set_speed(self, value):
        self._train.device.set_speed(int(value))

    def _capture_cruise(self):
        speed = self._train.device.speed
        if speed != 0:
            self._cruise_speed = speed

    def _apply_moving_speed(self, flip=False):
        self._capture_cruise()
        magnitude = abs(self._cruise_speed) if self._cruise_speed else FALLBACK_SPEED
        sign = 1 if self._cruise_speed >= 0 else -1
        if flip:
            sign = -sign
        speed = sign * magnitude
        self._cruise_speed = speed
        self._set_speed(speed)
        self._train.set_direction("reverse" if speed < 0 else "forward")

    def _cancel_task(self):
        if self._task and not self._task.done():
            self._task.cancel()
        self._task = None

    def _running_loop(self):
        try:
            return asyncio.get_running_loop()
        except RuntimeError:
            return None

    def _schedule_hold_retry(self):
        if self._running_loop() is None:
            return
        if self._task and not self._task.done():
            return
        self._task = asyncio.ensure_future(self._hold_retry_loop())

    async def _hold_retry_loop(self):
        try:
            while self._state == ExecutorState.HOLD:
                await asyncio.sleep(self._hold_retry_s)
                if self._state != ExecutorState.HOLD:
                    return
                self.try_depart()
        except asyncio.CancelledError:
            return

    def _schedule_wait(self, seconds):
        self._cancel_task()
        if self._running_loop() is None:
            self._advance_and_depart()
            return
        self._task = asyncio.ensure_future(self._wait_then_depart(seconds))

    async def _wait_then_depart(self, seconds):
        try:
            await asyncio.sleep(seconds)
            if self._state != ExecutorState.WAITING:
                return
            self._advance_and_depart()
        except asyncio.CancelledError:
            return

    def _release_current_leg(self):
        if self._current_leg is not None:
            self._network.release_leg(self._owner(), self._current_leg.segments)
            self._current_leg = None
        self._train.set_current_segment_ids([], "")

    def _hold(self, reason):
        already_holding = self._state == ExecutorState.HOLD
        self._set_speed(0)
        self._set_state(ExecutorState.HOLD, reason)
        if not already_holding:
            self._schedule_hold_retry()

    def _next_order(self):
        orders = self._train.orders
        if orders.rowCount() == 0:
            return None
        return orders.get(self._train.current_order_index)

    def _advance_and_depart(self):
        count = self._train.orders.rowCount()
        if count == 0:
            self._set_state(ExecutorState.IDLE)
            return
        self._train.set_current_order_index((self._train.current_order_index + 1) % count)
        self.try_depart()

    def _arrive(self, order):
        wait = float(order.wait_seconds) if order is not None else 0.0
        self._release_current_leg()
        if wait <= 0:
            self._advance_and_depart()
            return
        self._set_speed(0)
        self._set_state(ExecutorState.WAITING)
        self._schedule_wait(wait)

    @Slot()
    def try_depart(self):
        if self._state == ExecutorState.PAUSED:
            return
        if self._planner is None or self._network is None:
            return

        order = self._next_order()
        if order is None:
            self._set_speed(0)
            self._set_state(ExecutorState.IDLE)
            return

        current = self._train.current_node_id
        if not current:
            self._set_speed(0)
            self._set_state(ExecutorState.WAITING_FOR_LOCALIZATION)
            return

        previous = self._previous_node_id or None
        exclude = None
        if previous and not self._network.is_dead_end(current) and not self._train.allow_reverse:
            exclude = previous

        leg = self._planner.compute_leg(current, order.target_node_id, exclude_neighbor=exclude)
        if leg is None:
            unrestricted = self._planner.compute_leg(current, order.target_node_id)
            if unrestricted is None:
                self._hold("no path")
                return
            if not self._train.allow_reverse:
                self._hold("no reverse")
                return
            leg = unrestricted

        if len(leg.nodes) <= 1 or not leg.segments:
            if self._state == ExecutorState.WAITING:
                self._set_speed(0)
                return
            self._arrive(order)
            return

        first_hop = leg.nodes[1]
        reversing = self._network.is_reverse_depart(current, previous, first_hop)
        if reversing and not self._train.allow_reverse:
            self._hold("no reverse")
            return

        if not self._network.try_reserve_leg(self._owner(), leg.segments):
            self._hold("conflict")
            return

        self._current_leg = leg
        self._cancel_task()
        flip = reversing or (bool(previous) and self._network.is_dead_end(current))
        self._apply_moving_speed(flip=flip)
        self._train.set_current_segment_ids(leg.segments, f"{leg.nodes[0]}:{leg.nodes[-1]}")
        self._set_state(ExecutorState.MOVING)

    def on_marker(self, node_id):
        if not node_id:
            return

        old = self._train.current_node_id
        if old and old != node_id:
            self._previous_node_id = old
        self._train.set_current_node_id(node_id)

        if self._state == ExecutorState.PAUSED:
            return

        if self._state in (
            ExecutorState.IDLE,
            ExecutorState.WAITING_FOR_LOCALIZATION,
            ExecutorState.HOLD,
        ):
            self.try_depart()
            return

        if self._state != ExecutorState.MOVING:
            return

        order = self._next_order()
        if order is not None and node_id == order.target_node_id:
            self._arrive(order)

    @Slot()
    def pause(self):
        self._paused_while_waiting = self._state == ExecutorState.WAITING
        self._cancel_task()
        self._release_current_leg()
        if self._network is not None:
            self._network.release_all_for(self._owner())
        self._set_state(ExecutorState.PAUSED)

    @Slot()
    def resume(self):
        if self._network is not None:
            self._network.release_all_for(self._owner())
        self._train.set_current_segment_ids([], "")
        self._current_leg = None
        self._capture_cruise()
        if not self._train.current_node_id:
            self._paused_while_waiting = False
            self._set_speed(0)
            self._set_state(ExecutorState.WAITING_FOR_LOCALIZATION)
            return
        if self._paused_while_waiting:
            self._paused_while_waiting = False
            self._set_state(ExecutorState.IDLE)
            self._advance_and_depart()
            return
        self._set_state(ExecutorState.IDLE)
        self.try_depart()
