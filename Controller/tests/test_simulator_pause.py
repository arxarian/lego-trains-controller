from unittest.mock import MagicMock, patch

from PySide6.QtGui import QColor

from python.items.fake_device import FakeDevice, TRANSPARENT_COLOR
from python.simulator import Simulator


def _close_coro(coro):
    """ensure_future evaluates run_loop() before the mock runs; close the orphan coro."""
    coro.close()
    return MagicMock()


def test_fake_device_set_color_skips_duplicate_emit():
    device = FakeDevice()
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
    trains = MagicMock()
    sim = Simulator(network, trains)
    sim._circuit = [("nodeA", "#ff0000"), ("nodeB", "#00ff00"), ("nodeC", "#0000ff")]
    sim._current_index = 0
    sim._marker_consumed = True
    sim._fake_device = FakeDevice()
    sim._train = MagicMock()
    sim._train._current_segment_id = "nodeA:nodeB"
    sim.set_is_running(True)

    sim.pause_simulation()

    network.unreserve.assert_not_called()
    assert sim._train._current_segment_id == "nodeA:nodeB"
    assert sim.is_running is True
    assert sim._run_task is None
    assert sim._fake_device.color == TRANSPARENT_COLOR

    with patch("python.simulator.asyncio.ensure_future", side_effect=_close_coro) as ensure_future:
        sim.unpause_simulation()

    assert sim._current_index == 1
    assert sim._marker_consumed is False
    ensure_future.assert_called_once()


def test_unpause_does_not_start_second_loop_while_running():
    network = MagicMock()
    trains = MagicMock()
    sim = Simulator(network, trains)
    sim._circuit = [("nodeA", "#ff0000"), ("nodeB", "#00ff00")]
    sim.set_is_running(True)
    sim._fake_device = FakeDevice()
    first = MagicMock()
    first.done.return_value = False
    sim._run_task = first

    with patch("python.simulator.asyncio.ensure_future") as ensure_future:
        sim.unpause_simulation()

    ensure_future.assert_not_called()
    assert sim._run_task is first
    assert sim._current_index == 0
