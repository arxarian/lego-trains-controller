from __future__ import annotations

from PySide6.QtCore import QSortFilterProxyModel, Qt, Property, Signal
from PySide6.QtQml import QmlElement

from path_indicators import PathIndicators

QML_IMPORT_NAME = "TrainView"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class PathIndicatorsFilter(QSortFilterProxyModel):

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._path_id = ""

    def filterAcceptsRow(self, source_row, source_parent):
        model = self.sourceModel()
        index = model.index(source_row, 0, source_parent)

        path_indicator = model.data(index, PathIndicators.Role.ObjectRole)

        if not path_indicator:
            return False

        return self._path_id == path_indicator.path_id or path_indicator.path_id == ""

    def path_id(self):
        return self._path_id

    def set_path_id(self, value):
        self.beginFilterChange()
        self._path_id = value
        self.invalidateRowsFilter()
        self.path_id_changed.emit()

    path_id_changed = Signal()
    path_id = Property(str, path_id, set_path_id, notify=path_id_changed)
