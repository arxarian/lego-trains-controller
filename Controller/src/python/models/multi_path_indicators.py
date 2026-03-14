# This Python file uses the following encoding: utf-8
from __future__ import annotations

from PySide6.QtCore import QModelIndex

from python.items.multi_path_indicator import MultiPathIndicator
from python.models.object_based_model import ObjectBasedModel

DEFAULT_PATH = "A"

class MultiPathIndicators(ObjectBasedModel[MultiPathIndicator]):

    _item_class = MultiPathIndicator

    def __init__(self, parent=None):
        super().__init__(parent)

    def setModel(self, metaData):
        path_ids = set()
        for d in metaData:
            if "path_id" in d and d["path_id"] != None and d["path_id"] != "":  # add only named paths
                path_ids.add(d["path_id"])
        if len(path_ids) == 0:
            path_ids.add(DEFAULT_PATH)

        self.beginInsertRows(QModelIndex(), 0, len(path_ids) - 1)
        for id in path_ids:
            self._items.append(MultiPathIndicator(id=id, parent=self))
        self.endInsertRows()
