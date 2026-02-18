from __future__ import annotations

from enum import IntEnum
from typing import TypeVar, Generic, List, Type
from PySide6.QtCore import QAbstractListModel, QObject, Slot
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

    def roleNames(self):
        roles = super().roleNames()
        roles[ObjectBasedModel.Role.ObjectRole] = QByteArray(b"object")
        return roles

    def save_data(self) -> list:
        return [item.save_data() for item in self._items]

    # TODO - add load_metadata?

    @classmethod    # TODO - is there any meanful use?
    def load_data(cls, data, parent):
        return cls(data=data, parent=parent)

    def setModel(self, metaData: list):
        self.beginInsertRows(QModelIndex(), 0, len(metaData))
        for d in metaData:
            self._items.append(self._item_class(data=d, parent=self))
        self.endInsertRows()

    @Slot(result=int)
    def count(self):
        return self.rowCount()

    @Slot(int, result=QObject)
    def get(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None
