# This Python file uses the following encoding: utf-8

from __future__ import annotations

import json
from importlib import resources

from PySide6.QtCore import QModelIndex, Signal, Property

from python.items.marker_type import MarkerType
from python.models.object_based_model import ObjectBasedModel

class MarkerTypes(ObjectBasedModel[MarkerType]):

    _item_class = MarkerType

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._markersActive = False

        self.load_data()

    def load_data(self):
        with resources.open_text("resources", "marker_types.json") as json_data:
            data = json.load(json_data)

            self.beginInsertRows(QModelIndex(), 0, len(data))
            self._items = [MarkerType(data=d, parent=self) for d in data]
            self.endInsertRows()

    def markersActive(self):
        return self._markersActive

    def set_markersActive(self, value):
        self._markersActive = value
        self.markersActive_changed.emit()

    markersActive_changed = Signal()
    markersActive = Property(bool, markersActive, set_markersActive, notify=markersActive_changed)

