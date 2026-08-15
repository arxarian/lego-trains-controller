from __future__ import annotations

from PySide6.QtCore import Property, Signal, Slot

from python.models.object_based_model import ObjectBasedModel
from python.items.train import Train


class Trains(ObjectBasedModel[Train]):

    _item_class = Train

    def __init__(self, network, train_devices, planner=None, parent=None):
        super().__init__(parent)
        self._network = network
        self._planner = planner
        self._last_order_hint = ""
        train_devices.device_connected.connect(self.add_train)

    def add_train(self, device):
        train = Train(device=device, network=self._network, planner=self._planner, parent=self)
        device.disconnected.connect(lambda d: self.remove_by_device(d))
        self.append(train)
        return train

    def remove_by_device(self, device):
        train = next((t for t in self._items if t.device == device), None)
        if train is None:
            print(f"cannot remove train {train}, not in the list")
            return

        self.remove(train)

    def last_order_hint(self):
        return self._last_order_hint

    last_order_hint_changed = Signal()
    last_order_hint = Property(str, last_order_hint, notify=last_order_hint_changed)

    def _set_last_order_hint(self, message: str):
        print(f"Trains: {message}")
        if self._last_order_hint == message:
            return
        self._last_order_hint = message
        self.last_order_hint_changed.emit()

    @Slot(int, int, str, int, result=bool)
    def add_order_for_marker(self, train_index: int, rail_id: int, path_id: str, distance: int) -> bool:
        train = self.get(train_index)
        if train is None:
            self._set_last_order_hint("No planning-target train")
            return False

        node_id = self._network.node_id_for_marker(rail_id, path_id, distance)
        if not node_id:
            if not self._network.has_graph:
                self._set_last_order_hint("No graph")
            else:
                self._set_last_order_hint("Marker is not a graph node")
            return False

        train.add_order(node_id, 0.0)
        self._set_last_order_hint(f"Added order {node_id}")
        return True
