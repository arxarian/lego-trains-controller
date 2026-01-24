from __future__ import annotations

from enum import IntEnum
from PySide6.QtCore import QAbstractListModel, Slot, QEnum, Qt, QModelIndex, QByteArray
from PySide6.QtQml import QmlElement
#from PySide6.QtGui import QColor

from path_indicator import PathIndicator

QML_IMPORT_NAME = "TrainView"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class PathIndicators(QAbstractListModel):

    @QEnum
    class Role(IntEnum):
        ObjectRole = Qt.ItemDataRole.UserRole

    def __init__(self, data: list=None, parent=None) -> None:
        super().__init__(parent)
        self._data = data or [] # TODO - why? Is it needed?
        self._items = []

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
        self.beginInsertRows(QModelIndex(), 0, len(metaData))
        for i, d in enumerate(metaData):
            self._items.append(PathIndicator(data=d, parent=self))
        self.endInsertRows()
        self._data = [] # clear the original data, not needed anymore

    #def load_data(data, parent):
    #    return PathIndicators(data=data, parent=parent)
