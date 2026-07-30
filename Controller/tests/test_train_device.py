from unittest.mock import MagicMock

from python.items.train_device import TrainDevice
from python.items.train_device_sim import TrainDeviceSim
from python.items.train import Train

SHARED_PROPERTY_NAMES = (
    "name",
    "initialized",
    "color",
    "speed",
    "voltage",
    "minimalSpeed",
)


def test_train_device_sim_exposes_shared_property_names():
    device = TrainDeviceSim(name="sim")
    for name in SHARED_PROPERTY_NAMES:
        assert hasattr(device, name), name
    assert isinstance(device, TrainDevice)
    assert device.name == "sim"
    assert device.initialized is True
    assert device.minimalSpeed == 0


def test_train_accepts_train_device_sim():
    network = MagicMock()
    network.find_node_by_color.return_value = None
    device = TrainDeviceSim(name="sim")
    train = Train(device, network)
    assert train.device is device
