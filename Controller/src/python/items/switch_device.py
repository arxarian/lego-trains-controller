# This Python file uses the following encoding: utf-8
from __future__ import annotations

import asyncio

from PySide6.QtCore import QObject, Property, Signal, Slot

from python.items.rail import SWITCH_PATH_IDS, DEFAULT_SWITCH_POSITION


class SwitchDevice(QObject):
    """Switch actuator role: set turnout position A|B (sim or HW)."""

    disconnected = Signal(QObject)
    position_changed = Signal()
    initialized_changed = Signal()
    name_changed = Signal()
    bound_rail_changed = Signal()

    def __init__(self, name="unknown", *, initialized=False, parent=None):
        super().__init__(parent)
        self._name = name
        self._initialized = initialized
        self._position = DEFAULT_SWITCH_POSITION
        self._confirmed_position = DEFAULT_SWITCH_POSITION
        self._confirm_waiters: list[tuple[str, asyncio.Event]] = []
        self._bound_rail = None

    def role(self):
        return "switch"

    role = Property(str, role, constant=True)

    def name(self):
        return self._name

    def set_name(self, value):
        if self._name == value:
            return
        self._name = value
        self.name_changed.emit()

    name = Property(str, name, set_name, notify=name_changed)

    def initialized(self):
        return self._initialized

    def set_initialized(self, value):
        if self._initialized == value:
            return
        self._initialized = value
        self.initialized_changed.emit()

    initialized = Property(bool, initialized, set_initialized, notify=initialized_changed)

    def position(self):
        return self._position

    def set_position(self, value):
        if value not in SWITCH_PATH_IDS:
            return
        if self._position == value:
            return
        self._position = value
        self._confirmed_position = None
        self._apply_position(value)
        self.position_changed.emit()

    def _apply_position(self, value):
        """Subclass hook: update rail and/or send BLE."""
        pass

    position = Property(str, position, set_position, notify=position_changed)

    def is_confirmed(self, path_id: str) -> bool:
        return self._confirmed_position == path_id

    def _confirm_position(self, path_id: str):
        if path_id not in SWITCH_PATH_IDS or path_id != self._position:
            return
        self._confirmed_position = path_id
        remaining = []
        for wanted, event in self._confirm_waiters:
            if wanted == path_id:
                event.set()
            else:
                remaining.append((wanted, event))
        self._confirm_waiters = remaining

    async def wait_until_confirmed(self, path_id: str) -> bool:
        if self.is_confirmed(path_id):
            return True
        event = asyncio.Event()
        self._confirm_waiters.append((path_id, event))
        if self.is_confirmed(path_id):
            self._confirm_waiters = [(wanted, waiter) for wanted, waiter in self._confirm_waiters if waiter is not event]
            return True
        await event.wait()
        return self.is_confirmed(path_id)

    @Slot(str)
    def setPosition(self, path_id):
        self.set_position(path_id)

    def bound_rail(self):
        return self._bound_rail

    def set_bound_rail(self, rail):
        if self._bound_rail is rail:
            return
        self._bound_rail = rail
        self.bound_rail_changed.emit()

    bound_rail = Property(QObject, bound_rail, notify=bound_rail_changed)

    def boundRailId(self):
        if self._bound_rail is None:
            return -1
        return self._bound_rail.id

    boundRailId = Property(int, boundRailId, notify=bound_rail_changed)

    def boundRailLabel(self):
        if self._bound_rail is None:
            return "unassigned"
        return f"rail {self._bound_rail.id}"

    boundRailLabel = Property(str, boundRailLabel, notify=bound_rail_changed)

    def is_simulated(self):
        return False

    isSimulated = Property(bool, is_simulated, constant=True)

    @Slot()
    def disconnect(self):
        self.disconnected.emit(self)

    @Slot()
    def shutDown(self):
        self.disconnected.emit(self)
