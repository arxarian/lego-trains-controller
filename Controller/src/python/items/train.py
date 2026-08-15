from __future__ import annotations

from enum import IntEnum

from PySide6.QtCore import QObject, Property, Signal, Slot, QPointF, QEnum
from PySide6.QtQml import QmlElement

from python.items.order import Order
from python.models.orders import Orders
from python.plan_executor import PlanExecutor

QML_IMPORT_NAME = "TrainView"
QML_IMPORT_MAJOR_VERSION = 1


@QEnum
class ControlMode(IntEnum):
    Manual = 1
    Automatic = 2


@QmlElement
class Train(QObject):
    QEnum(ControlMode)

    def __init__(self, device, network, planner=None, parent=None):
        super().__init__(parent)
        self._device = device
        self._network = network
        self._planner = planner
        self._current_segment_ids = []
        self._leg_label = ""
        self._current_node_id = ""
        self._direction = "forward"
        self._position = QPointF()
        self._orders = Orders(parent=self)
        self._current_order_index = 0
        self._control_mode = ControlMode.Manual
        self._executor = PlanExecutor(self, planner, network, parent=self) if planner is not None else None

        device.color_changed.connect(self.on_color_changed)

    def on_color_changed(self):
        color = self._device.color
        if color.alpha() == 0:
            return

        self.set_direction("reverse" if self._device._speed < 0 else "forward")

        color_key = color.name()  # normalized lowercase hex e.g. "#ff0000"
        node_id = self._network.find_node_by_color(color_key)
        if node_id is None:
            print(f"Train: no marker node found for color {color_key}")
            return

        if self._control_mode == ControlMode.Automatic and self._executor is not None:
            self._executor.on_marker(node_id)
            return

        new_segment_ids, end_node = self._network.walk_to_next_marker(node_id, self._current_node_id or None)

        if not new_segment_ids or end_node is None:
            return

        owner = self._device.name
        for segment_id in self._current_segment_ids:
            self._network.release_segment(segment_id, owner)
        for segment_id in new_segment_ids:
            self._network.try_reserve_segment(segment_id, owner)

        self.set_current_node_id(node_id)
        self.set_current_segment_ids(new_segment_ids, f"{node_id}:{end_node}")
        print(f"Train '{owner}': reserved {new_segment_ids} via node {node_id}")

    def device(self):
        return self._device

    device = Property(QObject, device, constant=True)

    def position(self):
        return self._position

    def set_position(self, value):
        self._position = value
        self.position_changed.emit()

    def update_position(self):
        marker = self._network.find_node_marker(self._current_node_id)
        if marker:
            self.set_position(marker._position)
        else:
            print("marker {marker} not found")

    position_changed = Signal()
    position = Property(QPointF, position, set_position, notify=position_changed)

    def current_node_id(self):
        return self._current_node_id

    def set_current_node_id(self, value):
        self._current_node_id = value
        self.current_node_id_changed.emit()
        self.update_position()

    current_node_id_changed = Signal()
    current_node_id = Property(str, current_node_id, set_current_node_id, notify=current_node_id_changed)

    def current_segment_ids(self):
        return list(self._current_segment_ids)

    def set_current_segment_ids(self, value, leg_label: str | None = None):
        self._current_segment_ids = list(value) if value else []
        if leg_label is not None:
            self._leg_label = leg_label
        elif not self._current_segment_ids:
            self._leg_label = ""
        elif len(self._current_segment_ids) == 1:
            self._leg_label = self._current_segment_ids[0]
        self.current_segment_id_changed.emit()

    def current_segment_id(self):
        return self._leg_label

    def set_current_segment_id(self, value):
        if not value:
            self.set_current_segment_ids([], "")
            return
        self.set_current_segment_ids([s for s in str(value).split(";") if s], str(value))

    current_segment_id_changed = Signal()
    current_segment_id = Property(
        str, current_segment_id, set_current_segment_id, notify=current_segment_id_changed
    )

    def direction(self):
        return self._direction

    def set_direction(self, value):
        self._direction = value
        self.direction_changed.emit()

    direction_changed = Signal()
    direction = Property(str, direction, set_direction, notify=direction_changed)

    def orders(self):
        return self._orders

    orders = Property(QObject, orders, constant=True)

    def current_order_index(self):
        return self._current_order_index

    def set_current_order_index(self, value):
        value = int(value)
        if self._current_order_index != value:
            self._current_order_index = value
            self.current_order_index_changed.emit()

    current_order_index_changed = Signal()
    current_order_index = Property(
        int, current_order_index, set_current_order_index, notify=current_order_index_changed
    )

    def control_mode(self):
        return self._control_mode

    def set_control_mode(self, value):
        value = ControlMode(int(value))
        if self._control_mode != value:
            self._control_mode = value
            self.control_mode_changed.emit()
            if self._executor is not None:
                if value == ControlMode.Automatic:
                    self._executor.resume()
                else:
                    self._executor.pause()

    control_mode_changed = Signal()
    control_mode = Property(int, control_mode, set_control_mode, notify=control_mode_changed)

    def executor(self):
        return self._executor

    executor = Property(QObject, executor, constant=True)

    def _clamp_current_order_index(self):
        count = self._orders.rowCount()
        if count == 0:
            self.set_current_order_index(0)
        elif self._current_order_index >= count:
            self.set_current_order_index(count - 1)

    @Slot(str, float)
    def add_order(self, node_id: str, wait_seconds: float = 0.0):
        self._orders.append(Order(node_id, wait_seconds, parent=self._orders))

    @Slot(int)
    def remove_order(self, index: int):
        order = self._orders.get(index)
        if order is None:
            return

        self._orders.remove(order)
        if index < self._current_order_index:
            self.set_current_order_index(self._current_order_index - 1)
        else:
            self._clamp_current_order_index()

    @Slot(int, int)
    def move_order(self, from_index: int, to_index: int):
        if not self._orders.move(from_index, to_index):
            return

        current = self._current_order_index
        if current == from_index:
            self.set_current_order_index(to_index)
        elif from_index < current <= to_index:
            self.set_current_order_index(current - 1)
        elif to_index <= current < from_index:
            self.set_current_order_index(current + 1)

    @Slot()
    def clear_orders(self):
        self._orders.clear()
        self.set_current_order_index(0)

    @Slot(int, float)
    def set_wait(self, index: int, seconds: float):
        order = self._orders.get(index)
        if order is None:
            return
        order.set_wait_seconds(seconds)
