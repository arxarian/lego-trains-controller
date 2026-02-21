from pathlib import Path

import python.network as net
import python.models.project_storage as project

def test_load_file():
    data = project.loadDataFromFile(Path("tests/rails_big.json"))
    assert data and len(data) > 0

#def test_hello():
#    print("net.createNodeName()", net.createNodeName("5", "4"))
#    assert 5 != 5


