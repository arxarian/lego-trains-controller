from communication import Devices

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from pathlib import Path
import sys

if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    QGuiApplication.setOrganizationName("arProjects")
    QGuiApplication.setApplicationName("Lego Trains Controller")
    engine = QQmlApplicationEngine()
    devices = Devices()

    engine.addImportPath(Path(__file__).parent)
    engine.rootContext().setContextProperty("devices", devices)
    engine.loadFromModule("TrainsView", "Main")

    if not engine.rootObjects():
        sys.exit(-1)

    exit_code = app.exec()
    del engine
    sys.exit(exit_code)
