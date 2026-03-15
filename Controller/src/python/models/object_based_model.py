from __future__ import annotations

from enum import IntEnum
from typing import TypeVar, Generic, List, Type
from PySide6.QtCore import QAbstractListModel, QObject, Signal, Property, Slot
from PySide6.QtCore import QEnum, Qt, QModelIndex, QByteArray

T = TypeVar('T')

class ObjectBasedModel(QAbstractListModel, Generic[T]):

    _item_class: Type[T] = None

    @QEnum
    class Role(IntEnum):
        ObjectRole = Qt.ItemDataRole.UserRole + 1

    def __init__(self, data=[], parent=None) -> None:
        super().__init__(parent)

        if self._item_class is None:
            raise NotImplementedError(f"Class '{self.__class__.__name__}' has to define attribute '_item_class'. ")

        self._items: List[T] = []

        self.rowsInserted.connect(self._on_count_changed)
        self.rowsRemoved.connect(self._on_count_changed)
        self.modelReset.connect(self._on_count_changed)

    @Slot(result=list)
    def items(self):
        return self._items

    @Slot(QModelIndex, result=int)
    def rowCount(self, parent=QModelIndex()):
        return len(self._items)

    def data(self, index: QModelIndex, role: int):
        row = index.row()
        if row < self.rowCount():
            if role == ObjectBasedModel.Role.ObjectRole:
                return self._items[row]
        return None

    def clear(self):
        if self._items:
            self.beginRemoveRows(QModelIndex(), 0, len(self._items) - 1)
            self._items.clear()
            self.endRemoveRows()

    def roleNames(self):
        roles = super().roleNames()
        roles[ObjectBasedModel.Role.ObjectRole] = QByteArray(b"object")
        return roles

    def _on_count_changed(self, *args):
        self.count_changed.emit()

    count_changed = Signal()
    count = Property(int, lambda self: self.rowCount(), notify=count_changed)

    def append(self, item):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._items.append(item)
        self.endInsertRows()

    @Slot(int, result=QObject)
    def get(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None
