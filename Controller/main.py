from communication import Devices

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from qasync import QEventLoop

from pathlib import Path
import asyncio
import sys

if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    QGuiApplication.setOrganizationName("arProjects")
    QGuiApplication.setApplicationName("Lego Trains Controller")
    engine = QQmlApplicationEngine()
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    devices = Devices()

    engine.addImportPath(Path(__file__).parent)
    engine.rootContext().setContextProperty("devices", devices)
    engine.loadFromModule("TrainsView", "Main")

    if not engine.rootObjects():
        sys.exit(-1)

    with loop:  # TODO - why not to use app.exec()
        loop.run_forever()
