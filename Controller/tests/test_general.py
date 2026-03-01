from pathlib import Path

import python.models.project_storage as project

def test_load_file():
    data = project.loadDataFromFile(Path("tests/tracks/rails_big.json"))
    assert data and len(data) > 0
