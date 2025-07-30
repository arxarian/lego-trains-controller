from devices import Devices
from rails import Rails
from network import Network
from rotationdata import RotationData

import Railways.rails_rc

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from qasync import QEventLoop

from pathlib import Path
import asyncio
import sys, os

if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    QGuiApplication.setOrganizationName("arProjects")
    QGuiApplication.setApplicationName("Lego Trains Controller")
    engine = QQmlApplicationEngine()
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    devices = Devices()
    rails = Rails()
    network = Network()

    engine.addImportPath(Path(__file__).parent)
    engine.addImportPath(os.path.join(Path(__file__).parent, "TrainsView"))
    engine.addImportPath(os.path.join(Path(__file__).parent, "Railsways"))
    engine.rootContext().setContextProperty("devices", devices)
    engine.rootContext().setContextProperty("rails", rails)
    engine.rootContext().setContextProperty("network", network)
    engine.loadFromModule("TrainsView", "Main")

    if not engine.rootObjects():
        sys.exit(-1)

    with loop:  # TODO - why not to use app.exec()
        loop.run_forever()
