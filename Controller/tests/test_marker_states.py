import pytest
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication

from python.items.rail import Rail, RailType
from python.items.marker import MarkerState
from python.models.rails import Rails
from python.connectorregister import ConnectorRegister


@pytest.fixture(scope="session", autouse=True)
def ensure_qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def make_rails(*specs):
    """specs: (RailType, id) tuples -> (rails_model, [rail, ...])."""
    rails = Rails(ConnectorRegister())
    rails._items = [Rail(type=t, id=i, parent=rails) for (t, i) in specs]
    return rails


def connect(rail_a, index_a, rail_b, index_b):
    rail_a.connectTo(rail_b.id, index_a)
    rail_b.connectTo(rail_a.id, index_b)


def marker(rail, distance, path_id=None):
    return next((m for m in rail._markers._items
                 if m.distance == distance and (path_id is None or m.path_id == path_id)), None)


def take(rail, distance, path_id=None):
    marker(rail, distance, path_id).take(QColor("#ff0000"))


def remove(rail, distance, path_id=None):
    marker(rail, distance, path_id).remove()


def test_same_rail_proximity_blocking():
    rails = make_rails((RailType.Straight, 1))
    straight = rails.findRailData(1)

    take(straight, 8)

    assert marker(straight, 8).state == MarkerState.Taken
    assert marker(straight, 7).state == MarkerState.Blocked
    assert marker(straight, 9).state == MarkerState.Blocked
    assert marker(straight, 5).state == MarkerState.Free
    assert marker(straight, 11).state == MarkerState.Free


def test_boundary_overlap_lower_id_owns_tie():
    rails = make_rails((RailType.Straight, 1), (RailType.Straight, 2))
    a = rails.findRailData(1)
    b = rails.findRailData(2)

    connect(a, 1, b, 0)  # a.end (d16) <-> b.start (d0)

    # nothing taken: the higher-id rail's shared boundary point is blocked,
    # the lower-id rail keeps it free
    assert marker(b, 0).state == MarkerState.Blocked
    assert marker(a, 16).state == MarkerState.Free


def test_cross_rail_block_straight():
    rails = make_rails((RailType.Straight, 1), (RailType.Straight, 2))
    a = rails.findRailData(1)
    b = rails.findRailData(2)

    connect(a, 1, b, 0)

    take(a, 16)

    assert marker(b, 0).state == MarkerState.Blocked
    assert marker(b, 1).state == MarkerState.Blocked
    assert marker(b, 3).state == MarkerState.Free


def test_cross_rail_unblock_on_remove():
    rails = make_rails((RailType.Straight, 1), (RailType.Straight, 2))
    a = rails.findRailData(1)
    b = rails.findRailData(2)

    connect(a, 1, b, 0)

    take(a, 16)
    assert marker(b, 1).state == MarkerState.Blocked

    remove(a, 16)
    assert marker(b, 1).state == MarkerState.Free


def test_cross_rail_offset_marker():
    rails = make_rails((RailType.Straight, 1), (RailType.Straight, 2))
    a = rails.findRailData(1)
    b = rails.findRailData(2)

    connect(a, 1, b, 0)

    take(a, 15)

    assert marker(b, 0).state == MarkerState.Blocked
    assert marker(b, 1).state == MarkerState.Free


def test_cross_rail_curved():
    rails = make_rails((RailType.Straight, 1), (RailType.Curved, 2))
    a = rails.findRailData(1)
    c = rails.findRailData(2)

    connect(a, 1, c, 0)  # a.end (d16) <-> curved.start (d0)

    take(a, 16)

    assert marker(c, 0).state == MarkerState.Blocked
    assert marker(c, 1).state == MarkerState.Blocked
    assert marker(c, 3).state == MarkerState.Free


def test_switch_path_id_filtering():
    rails = make_rails((RailType.SwitchLeft, 1), (RailType.Straight, 2))
    switch = rails.findRailData(1)
    straight = rails.findRailData(2)

    connect(switch, 2, straight, 0)  # switch.end_straight (d32, path A) <-> straight.start (d0)

    take(straight, 1)

    # path A markers across the boundary are blocked
    assert marker(switch, 32, "A").state == MarkerState.Blocked
    # path B markers sharing nearby distances are unaffected
    assert marker(switch, 34, "B").state == MarkerState.Free
    assert marker(switch, 35, "B").state == MarkerState.Free
