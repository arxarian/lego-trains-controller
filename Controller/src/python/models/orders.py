from __future__ import annotations

from PySide6.QtCore import QModelIndex

from python.models.object_based_model import ObjectBasedModel
from python.items.order import Order


class Orders(ObjectBasedModel[Order]):

    _item_class = Order

    def move(self, from_index: int, to_index: int) -> bool:
        count = len(self._items)
        if from_index == to_index:
            return True
        if not (0 <= from_index < count) or not (0 <= to_index < count):
            return False

        # Qt beginMoveRows destination is the index before removal for moves downward.
        destination = to_index + 1 if to_index > from_index else to_index
        if not self.beginMoveRows(QModelIndex(), from_index, from_index, QModelIndex(), destination):
            return False

        item = self._items.pop(from_index)
        self._items.insert(to_index, item)
        self.endMoveRows()
        return True
