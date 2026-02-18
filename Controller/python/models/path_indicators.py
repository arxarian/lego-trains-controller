from __future__ import annotations

from PySide6.QtCore import Property, QObject, Signal, QModelIndex
from PySide6.QtQml import QmlElement

from python.items.path_indicator import PathIndicator
from python.models.multi_path_indicators import MultiPathIndicators
from python.models.object_based_model import ObjectBasedModel

QML_IMPORT_NAME = "TrainView"
QML_IMPORT_MAJOR_VERSION = 1

DEFAULT_ACTIVE_PATH = "A"

@QmlElement
class PathIndicators(ObjectBasedModel[PathIndicator]):

    _item_class = PathIndicator

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._path_id_active = ""
        self._multi_path_indicators = MultiPathIndicators(parent=self)

    def multiPathIndicators(self):
        return self._multi_path_indicators

    multiPathIndicators = Property(QObject, multiPathIndicators, constant=True)

    def setModel(self, metaData):
        self._multi_path_indicators.setModel(metaData)
        super().setModel(metaData)

    def path_id_active(self):
        return self._path_id_active

    def set_path_id_active(self, value):
        value = value if value != "" else DEFAULT_ACTIVE_PATH   # set the default active path if empty

        self._path_id_active = value
        self.path_id_active_changed.emit()

    path_id_active_changed = Signal()
    path_id_active = Property(str, path_id_active, set_path_id_active, notify=path_id_active_changed)
