import sys

import resources.rails_rc

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from qasync import QEventLoop
from pathlib import Path
import asyncio

from python.app_context import AppContext

def importPaths(engine: QQmlApplicationEngine):
    engine.addImportPath(Path(__file__).parent)
    engine.addImportPath("qml")
    engine.addImportPath("resources")

if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    QGuiApplication.setOrganizationName("arProjects")
    QGuiApplication.setApplicationName("Lego Trains Controller")
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    engine = QQmlApplicationEngine()
    importPaths(engine)
    context = AppContext(engine)

    def _on_about_to_quit():
        # Drop the QML tree while AppContext backends are still alive so
        # bindings are not re-evaluated against cleared context properties.
        for obj in list(engine.rootObjects()):
            obj.deleteLater()

    app.aboutToQuit.connect(_on_about_to_quit)

    engine.load(str("src/qml/Main.qml"))

    if not engine.rootObjects():
        sys.exit(-1)

    with loop:  # TODO - why not to use app.exec()
        loop.run_forever()

    # Destroy QML while AppContext (and its context properties) still exist.
    del engine
