from pathlib import Path
from unittest.mock import MagicMock

import pytest
from PySide6.QtWidgets import QApplication

import python.network_manager as net
import python.models.project_storage as project
from python.items.rail import Rail

TEST_TRACK = "tests/tracks/rails.json"
SEGMENT_ID = "3A16:6A8"


@pytest.fixture(scope="session", autouse=True)
def ensure_qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def net_manager():
    data = project.loadDataFromFile(Path(TEST_TRACK))
    rails = [Rail.load_data(d) for d in data.get("rails", [])]
    mock_rails = MagicMock()
    mock_rails.items.return_value = rails
    manager = net.NetworkManager(mock_rails)
    manager.generate()
    return manager


def test_two_owners_cannot_hold_same_segment(net_manager):
    assert net_manager.try_reserve_segment(SEGMENT_ID, "train-a")
    assert net_manager.owner_of(SEGMENT_ID) == "train-a"
    assert not net_manager.try_reserve_segment(SEGMENT_ID, "train-b")
    assert net_manager.owner_of(SEGMENT_ID) == "train-a"


def test_same_owner_rereserve_is_idempotent(net_manager):
    assert net_manager.try_reserve_segment(SEGMENT_ID, "train-a")
    assert net_manager.try_reserve_segment(SEGMENT_ID, "train-a")
    assert net_manager.owner_of(SEGMENT_ID) == "train-a"


def test_only_owner_can_release(net_manager):
    assert net_manager.try_reserve_segment(SEGMENT_ID, "train-a")
    assert not net_manager.release_segment(SEGMENT_ID, "train-b")
    assert net_manager.owner_of(SEGMENT_ID) == "train-a"

    assert net_manager.release_segment(SEGMENT_ID, "train-a")
    assert net_manager.owner_of(SEGMENT_ID) is None
    assert net_manager.try_reserve_segment(SEGMENT_ID, "train-b")
    assert net_manager.owner_of(SEGMENT_ID) == "train-b"


def test_release_all_for_frees_owner_segments(net_manager):
    segment_ids = list(net_manager.segments().keys())[:2]
    assert len(segment_ids) == 2

    for segment_id in segment_ids:
        assert net_manager.try_reserve_segment(segment_id, "train-a")
    other = [sid for sid in net_manager.segments() if sid not in segment_ids][0]
    assert net_manager.try_reserve_segment(other, "train-b")

    net_manager.release_all_for("train-a")

    for segment_id in segment_ids:
        assert net_manager.owner_of(segment_id) is None
    assert net_manager.owner_of(other) == "train-b"


def test_try_reserve_unknown_segment_fails(net_manager):
    assert not net_manager.try_reserve_segment("XXX", "train-a")
    assert net_manager.owner_of("XXX") is None


def test_generate_clears_owners(net_manager):
    assert net_manager.try_reserve_segment(SEGMENT_ID, "train-a")
    net_manager.generate()
    assert net_manager.owner_of(SEGMENT_ID) is None


def _two_segments(net_manager):
    segment_ids = list(net_manager.segments().keys())[:2]
    assert len(segment_ids) == 2
    return segment_ids


def test_try_reserve_leg_blocks_other_owner(net_manager):
    leg = _two_segments(net_manager)
    assert net_manager.try_reserve_leg("train-a", leg)
    assert all(net_manager.owner_of(sid) == "train-a" for sid in leg)

    assert not net_manager.try_reserve_leg("train-b", leg)
    assert all(net_manager.owner_of(sid) == "train-a" for sid in leg)


def test_release_leg_then_other_owner_succeeds(net_manager):
    leg = _two_segments(net_manager)
    assert net_manager.try_reserve_leg("train-a", leg)
    assert net_manager.release_leg("train-a", leg)
    assert all(net_manager.owner_of(sid) is None for sid in leg)

    assert net_manager.try_reserve_leg("train-b", leg)
    assert all(net_manager.owner_of(sid) == "train-b" for sid in leg)


def test_try_reserve_leg_partial_overlap_is_atomic(net_manager):
    s1, s2 = _two_segments(net_manager)
    assert net_manager.try_reserve_segment(s1, "train-a")

    assert not net_manager.try_reserve_leg("train-b", [s1, s2])
    assert net_manager.owner_of(s1) == "train-a"
    assert net_manager.owner_of(s2) is None


def test_try_reserve_leg_idempotent_for_same_owner(net_manager):
    leg = _two_segments(net_manager)
    assert net_manager.try_reserve_leg("train-a", leg)
    assert net_manager.try_reserve_leg("train-a", leg)
    assert all(net_manager.owner_of(sid) == "train-a" for sid in leg)


def test_try_reserve_leg_empty_succeeds(net_manager):
    assert net_manager.try_reserve_leg("train-a", [])
    assert net_manager.try_reserve_leg("train-a", None)


def test_try_reserve_leg_unknown_segment_fails_atomically(net_manager):
    s1 = _two_segments(net_manager)[0]
    assert not net_manager.try_reserve_leg("train-a", [s1, "XXX"])
    assert net_manager.owner_of(s1) is None
    assert net_manager.owner_of("XXX") is None
