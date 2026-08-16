import pytest
from PySide6.QtWidgets import QApplication

from python.items.rail import ControlMode, Rail, RailType


@pytest.fixture(scope="session", autouse=True)
def ensure_qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def test_switch_default_position_a():
    switch = Rail(type=RailType.SwitchLeft, id=1)

    assert switch.switch_position == "A"
    assert switch.path_indicators.path_id_active == "A"


def test_switch_set_position_b():
    switch = Rail(type=RailType.SwitchRight, id=2)

    switch.setSwitchPosition("B")

    assert switch.switch_position == "B"
    assert switch.path_indicators.path_id_active == "B"


def test_switch_toggle_position():
    switch = Rail(type=RailType.SwitchLeft, id=3)

    switch.toggleSwitchPosition()
    assert switch.switch_position == "B"
    assert switch.path_indicators.path_id_active == "B"

    switch.toggleSwitchPosition()
    assert switch.switch_position == "A"
    assert switch.path_indicators.path_id_active == "A"


def test_non_switch_set_position_noop():
    straight = Rail(type=RailType.Straight, id=4)
    assert straight.path_indicators.path_id_active == ""

    straight.setSwitchPosition("B")
    straight.toggleSwitchPosition()

    assert straight.switch_position == "A"
    assert straight.path_indicators.path_id_active == ""


def test_switch_ignores_invalid_path_id():
    switch = Rail(type=RailType.SwitchLeft, id=5)

    switch.setSwitchPosition("C")
    switch.setSwitchPosition("")

    assert switch.switch_position == "A"
    assert switch.path_indicators.path_id_active == "A"


def test_switch_default_mode_manual_unlocked():
    switch = Rail(type=RailType.SwitchLeft, id=6)

    assert switch.control_mode == ControlMode.Manual
    assert not switch.locked
    assert switch.locked_by == ""


def test_switch_toggle_rejected_in_automatic():
    switch = Rail(type=RailType.SwitchLeft, id=7)
    switch.set_control_mode(ControlMode.Automatic)

    switch.toggleSwitchPosition()

    assert switch.switch_position == "A"
    assert switch.path_indicators.path_id_active == "A"


def test_switch_toggle_rejected_when_locked():
    switch = Rail(type=RailType.SwitchLeft, id=8)
    switch.lock_for("train-a")

    switch.toggleSwitchPosition()

    assert switch.switch_position == "A"
    assert switch.locked
    assert switch.locked_by == "train-a"


def test_switch_set_position_works_while_locked():
    switch = Rail(type=RailType.SwitchLeft, id=9)
    switch.lock_for("train-a")

    switch.set_switch_position("B")

    assert switch.switch_position == "B"
    assert switch.path_indicators.path_id_active == "B"
    assert switch.locked


def test_switch_unlock_for_only_matching_owner():
    switch = Rail(type=RailType.SwitchLeft, id=10)
    switch.lock_for("train-a")

    switch.unlock_for("train-b")
    assert switch.locked
    assert switch.locked_by == "train-a"

    switch.unlock_for("train-a")
    assert not switch.locked
    assert switch.locked_by == ""
