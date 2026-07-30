import pytest
from PySide6.QtWidgets import QApplication

from python.items.rail import Rail, RailType


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
