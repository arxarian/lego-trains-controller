from __future__ import annotations

from enum import IntEnum
from PySide6.QtCore import QAbstractListModel, Slot, QEnum, Qt, QModelIndex, QByteArray, Property, QObject, Signal
from PySide6.QtQml import QmlElement

from python.items.path_indicator import PathIndicator
from python.models.multi_path_indicators import MultiPathIndicators

QML_IMPORT_NAME = "TrainView"
QML_IMPORT_MAJOR_VERSION = 1

DEFAULT_ACTIVE_PATH = "A"

@QmlElement
class PathIndicators(QAbstractListModel):

    @QEnum
    class Role(IntEnum):
        ObjectRole = Qt.ItemDataRole.UserRole

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._items = []
        self._path_id_active = ""
        self._multi_path_indicators = MultiPathIndicators(parent=self)

    def multiPathIndicators(self):
        return self._multi_path_indicators

    multiPathIndicators = Property(QObject, multiPathIndicators, constant=True)

    @Slot(QModelIndex, result=int)
    def rowCount(self, parent=QModelIndex()):
        return len(self._items)

    def data(self, index: QModelIndex, role: int):
        row = index.row()
        if row < self.rowCount():
            if role == PathIndicators.Role.ObjectRole:
                return self._items[row]
        return None

    def roleNames(self):
        roles = super().roleNames()
        roles[PathIndicators.Role.ObjectRole] = QByteArray(b"object")
        return roles

    def setModel(self, metaData):
        self._multi_path_indicators.setModel(metaData)
        self.beginInsertRows(QModelIndex(), 0, len(metaData))
        for d in metaData:
            self._items.append(PathIndicator(data=d, parent=self))
        self.endInsertRows()

    def path_id_active(self):
        return self._path_id_active

    def set_path_id_active(self, value):
        value = value if value != "" else DEFAULT_ACTIVE_PATH   # set the default active path if empty

        self._path_id_active = value
        self.path_id_active_changed.emit()

    path_id_active_changed = Signal()
    path_id_active = Property(str, path_id_active, set_path_id_active, notify=path_id_active_changed)
