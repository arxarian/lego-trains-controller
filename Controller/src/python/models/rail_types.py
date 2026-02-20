# This Python file uses the following encoding: utf-8

from __future__ import annotations

import json

from PySide6.QtCore import QModelIndex, Signal, Property

from python.items.rail_type import RailType
from python.models.object_based_model import ObjectBasedModel

class RailTypes(ObjectBasedModel[RailType]):

    _item_class = RailType

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._railsActive = True

        self.load_data()

    def load_data(self):
        with open("resources/rail_types.json") as json_data:
            data = json.load(json_data)

            self.beginInsertRows(QModelIndex(), 0, len(data))
            self._items = [RailType(data=d, parent=self) for d in data]
            self.endInsertRows()

    def railsActive(self):
        return self._railsActive

    def set_railsActive(self, value):
        self._railsActive = value
        self.railsActive_changed.emit()

    railsActive_changed = Signal()
    railsActive = Property(bool, railsActive, set_railsActive, notify=railsActive_changed)
