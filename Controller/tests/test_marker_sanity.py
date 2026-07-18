from pathlib import Path
from unittest.mock import MagicMock

import pytest
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication

import python.network_manager as net
import python.models.project_storage as project
from python.items.rail import Rail
from python.items.marker import MarkerState


@pytest.fixture(scope="session", autouse=True)
def ensure_qapp():
    app = QApplication.instance() or QApplication([])
    yield app


TEST_TRACK = "tests/tracks/rails.json"


def _manager_from_track(path=TEST_TRACK):
    data = project.loadDataFromFile(Path(path))
    rails = [Rail.load_data(d) for d in data.get("rails", [])]
    mock_rails = MagicMock()
    mock_rails.items.return_value = rails
    return net.NetworkManager(mock_rails), rails


def _graph_markers(manager):
    return manager._collect_graph_markers()


def _force_take(rail, distance, color, path_id=None):
    marker = next(
        m for m in rail.markers._items
        if m.distance == distance and (path_id is None or m.path_id in (None, "", path_id))
    )
    marker.set_color(QColor(color))
    marker.set_state(MarkerState.Taken)
    return marker


def test_unique_layout_no_warnings():
    manager, _ = _manager_from_track()
    manager.generate()

    markers = _graph_markers(manager)
    unique_nodes = {m["node_id"] for m in markers}
    unique_colors = {m["color_key"] for m in markers}
    assert len(unique_nodes) > 0
    assert len(unique_colors) == len(unique_nodes)
    assert manager.markerWarnings == []
    assert len(manager._color_map) == len(unique_nodes)


def test_duplicate_color_warning():
    manager, rails = _manager_from_track()
    manager.generate()
    markers = _graph_markers(manager)
    assert len(markers) >= 2

    first, second = markers[0], markers[1]
    first_rail = next(r for r in rails if r.id == first["rail_id"])
    second_rail = next(r for r in rails if r.id == second["rail_id"])
    _force_take(first_rail, first["distance"], "#ff0000", first["path_id"])
    _force_take(second_rail, second["distance"], "#ff0000", second["path_id"])

    manager.generate()

    warnings = manager.markerWarnings
    assert any(w.startswith("Duplicate marker color #ff0000") for w in warnings)
    assert manager._color_map.get("#ff0000") is not None
    # first-write wins: map has one entry for the color
    assert sum(1 for k in manager._color_map if k == "#ff0000") == 1
