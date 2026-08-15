from unittest.mock import MagicMock, patch

from PySide6.QtGui import QColor

from python.items.train_device import TRANSPARENT_COLOR
from python.items.train_device_sim import TrainDeviceSim
from python.simulator import Simulator


def _close_coro(coro):
    """ensure_future evaluates run_loop() before the mock runs; close the orphan coro."""
    coro.close()
    return MagicMock()


def test_sim_device_set_color_skips_duplicate_emit():
    device = TrainDeviceSim()
    emissions = []
    device.color_changed.connect(lambda: emissions.append(device.color))

    red = QColor("#ff0000")
    device.set_color(red)
    device.set_color(red)
    device.set_color(TRANSPARENT_COLOR)
    device.set_color(TRANSPARENT_COLOR)

    assert len(emissions) == 2
    assert emissions[0] == red
    assert emissions[1] == TRANSPARENT_COLOR


def test_pause_keeps_reservation_and_resume_skips_consumed_marker():
    network = MagicMock()
    network.find_next_marker_node.return_value = "nodeB"
    trains = MagicMock()
    sim = Simulator(network, trains)
    sim._current_node_id = "nodeA"
    sim._previous_node_id = None
    sim._marker_consumed = True
    sim._sim_device = TrainDeviceSim()
    sim._train = MagicMock()
    sim._train._current_segment_ids = ["nodeA:nodeB"]
    sim.set_is_running(True)

    sim.pause_simulation()

    network.unreserve.assert_not_called()
    network.unreserve_segments.assert_not_called()
    assert sim._train._current_segment_ids == ["nodeA:nodeB"]
    assert sim.is_running is True
    assert sim._run_task is None
    assert sim._sim_device.color == TRANSPARENT_COLOR

    with patch("python.simulator.asyncio.ensure_future", side_effect=_close_coro) as ensure_future:
        sim.unpause_simulation()

    network.find_next_marker_node.assert_called_with("nodeA", None)
    assert sim._current_node_id == "nodeB"
    assert sim._previous_node_id == "nodeA"
    assert sim._marker_consumed is False
    ensure_future.assert_called_once()


def test_unpause_does_not_start_second_loop_while_running():
    network = MagicMock()
    trains = MagicMock()
    sim = Simulator(network, trains)
    sim._current_node_id = "nodeA"
    sim.set_is_running(True)
    sim._sim_device = TrainDeviceSim()
    first = MagicMock()
    first.done.return_value = False
    sim._run_task = first

    with patch("python.simulator.asyncio.ensure_future") as ensure_future:
        sim.unpause_simulation()

    ensure_future.assert_not_called()
    assert sim._run_task is first
    assert sim._current_node_id == "nodeA"


def test_negative_speed_advances_to_previous_marker():
    network = MagicMock()
    sim = Simulator(network, MagicMock())
    sim._current_node_id = "nodeB"
    sim._previous_node_id = "nodeA"
    sim._sim_device = TrainDeviceSim()
    sim._sim_device.set_speed(-40)

    assert sim._advance_to_next_marker() is True
    assert sim._current_node_id == "nodeA"
    assert sim._previous_node_id == "nodeB"
    network.find_next_marker_node.assert_not_called()


def test_step_delay_uses_abs_speed():
    sim = Simulator(MagicMock(), MagicMock())
    sim._sim_device = TrainDeviceSim()
    sim._sim_device.set_speed(-50)
    sim.onSpeedChanged()
    assert sim._step_delay == 40 / 50
