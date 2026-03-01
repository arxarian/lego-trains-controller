#import networkx as nx
from pathlib import Path
from unittest.mock import MagicMock

import python.network_manager as net
import python.models.project_storage as project
from python.items.rail import Rail

TEST_TRACK = "tests/tracks/rails.json"

def test_generate_segments():
    data = project.loadDataFromFile(Path(TEST_TRACK))
    assert data and len(data) > 0

    raw_rails = data.get("rails", [])
    rails = [Rail.load_data(d) for d in raw_rails]
    assert len(rails) > 0

    mock_rails = MagicMock()
    mock_rails.items.return_value = rails

    net_manager = net.NetworkManager(mock_rails)
    net_manager.generate()
    net_manager.reserve("3A16:6A8")

