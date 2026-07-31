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


def test_current_segment_id_shows_path_endpoints():
    network = MagicMock()
    device = TrainDeviceSim(name="sim")
    train = Train(device, network)

    assert train.current_segment_id == ""

    train.set_current_segment_ids(["13A12:13-24"])
    assert train.current_segment_id == "13A12:13-24"

    train._current_node_id = "13A12"
    train.set_current_segment_ids([
        "13-24:13A12",
        "13-24:24-32",
        "24-32:28A16",
    ])
    assert train.current_segment_id == "13A12:28A16"
