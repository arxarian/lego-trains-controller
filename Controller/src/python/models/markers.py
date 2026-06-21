from __future__ import annotations

from PySide6.QtCore import Slot, QModelIndex
from PySide6.QtQml import QmlElement
from PySide6.QtGui import QColor

from python.items.connector import State
from python.items.marker import Marker, MarkerState
from python.models.object_based_model import ObjectBasedModel

QML_IMPORT_NAME = "TrainView"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class Markers(ObjectBasedModel[Marker]):

    _item_class = Marker

    def __init__(self, data: list=None, parent=None) -> None:
        super().__init__(parent)
        self._data = data or []
        self.rail = None    # TODO - add _
        self._connectors = None

    def resolveColor(self, index):
        color = next((d["color"] for d in self._data if d["index"] == index), None)
        return None if color is None else QColor(color)

    def setModel(self, metaData):
        self.beginInsertRows(QModelIndex(), 0, len(metaData) - 1)
        for i, d in enumerate(metaData):
            self._items.append(Marker(data=d, index=i, color=self.resolveColor(i) , parent=self))
        self.endInsertRows()
        self._data = [] # clear the original data, not needed anymore

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

    def updateStates(self):
        def atProximity(marker1, marker2):
            return abs(marker1.distance - marker2.distance) == 1

        def taken_marker_at_proximity(markers, marker):
            return any(m.taken for m in markers if atProximity(marker, m))

        def connected_rail_from_marker(connectors, marker):
            return connectors.getByName(marker.connector).connectedRailId

        # for all markers
        for marker in self._items:
            if marker.taken:
                continue

            # if there is a taken marker at proximity, blocked this one
            new_state = MarkerState.Free
            if taken_marker_at_proximity(self._items, marker):
                new_state = MarkerState.Blocked
            marker.state = new_state

            # if two rails are connected, the one with lower id has blocked boundary marker point
            if marker.at_boundary():
                connectedRailId = connected_rail_from_marker(self._connectors, marker)

                if connectedRailId == State.NotConnected:
                    continue

                if not marker.taken:
                    marker.state = MarkerState.Blocked if connectedRailId > self.rail.id else MarkerState.Free

                # no need to go further if blocked
                if marker.blocked:
                    continue

                # I need the overlapping marker from the connected rail
                rails_model = self.rail.parent() # TODO - fix parent of parent...
                connected_rail = rails_model.findRailData(connectedRailId)
                close_markers = connected_rail._markers._items
                close_connectors = connected_rail._connectors

                # loop markers at boundary and compare if that marker reference a connector connected to this rail
                for close_marker in connected_rail._markers._items:
                    if close_marker.at_boundary():
                        print("close_marker", close_marker.distance, connected_rail_from_marker(close_connectors, close_marker),
                            self.rail.id, connected_rail_from_marker(self._connectors, marker))
                        if connected_rail_from_marker(close_connectors, close_marker) == self.rail.id:
                            print("got it!")
                            if taken_marker_at_proximity(close_markers, close_marker):
                                 marker.state = MarkerState.Blocked
                                 break

    @Slot(result=int)
    def activeCount(self, path_id = None):
        if path_id == None:
            return sum(1 for item in self._items if item.taken)
        else:
            return sum(1 for item in self._items if item.taken and item.path_id in (None, "", path_id))
