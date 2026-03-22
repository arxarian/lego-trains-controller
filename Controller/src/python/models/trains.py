from __future__ import annotations

from python.models.object_based_model import ObjectBasedModel
from python.items.train import Train

class Trains(ObjectBasedModel[Train]):

    _item_class = Train

    def __init__(self, network, devices, parent=None):
        super().__init__(parent)
        self._network = network
        devices.device_connected.connect(self.add_train)

    def add_train(self, device):
        train = Train(device=device, network=self._network, parent=self)
        device.disconnected.connect(lambda d: self.remove_by_device(d))
        self.append(train)
        return train

    def remove_by_device(self, device):
        train = next((t for t in self._items if t.device == device), None)
        if train is None:
            print(f"cannot remove train {train}, not in the list")
            return

        self.remove(train)
