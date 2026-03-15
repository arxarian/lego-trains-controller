from __future__ import annotations

from PySide6.QtCore import QObject, Property, Signal
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "TrainView"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class Train(QObject):

    def __init__(self, device, network, parent=None):
        super().__init__(parent)
        self._device = device
        self._network = network
        self._current_segment_id = ""
        self._current_node_id = ""
        self._direction = "forward"

        device.color_changed.connect(self._on_color_changed)

    def _on_color_changed(self):
        color = self._device.color
        if color.alpha() == 0:
            return

        self.set_direction("reverse" if self._device._speed < 0 else "forward")

        color_key = color.name()  # normalized lowercase hex e.g. "#ff0000"
        node_id = self._network.find_node_by_color(color_key)
        if node_id is None:
            print(f"Train: no marker node found for color {color_key}")
            return

        new_segment_id = self._network.find_segment_by_entry_node(node_id, self._current_node_id)
        if new_segment_id is None:
            return

        if self._current_segment_id:
            self._network.unreserve(self._current_segment_id)

        self._network.reserve(new_segment_id)

        self._current_node_id = node_id
        self.set_current_segment_id(new_segment_id)
        print(f"Train '{self._device.name}': entered segment {new_segment_id} via node {node_id}")

    def device(self):
        return self._device

    device = Property(QObject, device, constant=True)

    def current_segment_id(self):
        return self._current_segment_id

    def set_current_segment_id(self, value):
        self._current_segment_id = value
        self.current_segment_id_changed.emit()

    current_segment_id_changed = Signal()
    current_segment_id = Property(str, current_segment_id, set_current_segment_id,
                                  notify=current_segment_id_changed)

    def direction(self):
        return self._direction

    def set_direction(self, value):
        self._direction = value
        self.direction_changed.emit()

    direction_changed = Signal()
    direction = Property(str, direction, set_direction, notify=direction_changed)
