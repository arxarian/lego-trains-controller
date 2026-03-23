from __future__ import annotations

from PySide6.QtCore import Slot, QModelIndex
from PySide6.QtQml import QmlElement
from PySide6.QtGui import QColor

from python.items.marker import Marker
from python.models.object_based_model import ObjectBasedModel

QML_IMPORT_NAME = "TrainView"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class Markers(ObjectBasedModel[Marker]):

    _item_class = Marker

    def __init__(self, data: list=None, parent=None) -> None:
        super().__init__(parent)
        self._data = data or []

    def resolveColor(self, index):
        color = next((d["color"] for d in self._data if d["index"] == index), None)
        return None if color is None else QColor(color)

    def setModel(self, metaData):
        self.beginInsertRows(QModelIndex(), 0, len(metaData) - 1)
        for i, d in enumerate(metaData):
            self._items.append(Marker(data=d, index=i, color=self.resolveColor(i) , parent=self))
        self.endInsertRows()
        self._data = [] # clear the original data, not needed anymore
        self.updateEnabledStates()

    def save_data(self):
        data = [
            marker_data
            for marker in self._items
            if (marker_data := marker.save_data())
        ]
        return data

    def load_data(data, parent):
        return Markers(data=data, parent=parent)

    def _path_ids_compatible(self, pid1, pid2):
        if pid1 in (None, "") or pid2 in (None, ""):
            return True
        return pid1 == pid2

    def updateEnabledStates(self):
        visible_markers = [m for m in self._items if m.visible]
        for marker in self._items:
            if marker.visible:
                continue
            blocked = any(
                abs(v.distance - marker.distance) == 1
                and self._path_ids_compatible(marker.path_id, v.path_id)
                for v in visible_markers
            )
            marker.set_enabled(not blocked)

    @Slot(result=int)
    def activeCount(self, path_id = None):
        if path_id == None:
            return sum(1 for item in self._items if item.visible)
        else:
            return sum(1 for item in self._items if item.visible and item.path_id in (None, "", path_id))
