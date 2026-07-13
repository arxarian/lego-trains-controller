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

    def path_ids_compatible(self, pid1, pid2):
        if pid1 in (None, "") or pid2 in (None, ""):
            return True
        return pid1 == pid2

    def updateStates(self):
        self.updateStatesLocally()

        # a marker placed/removed at a shared boundary also affects the connected
        # rail's markers, so recompute every connected rail (own state only)
        rails_model = self.rail.parent()
        for connectedRailId in self.connectedRailIds():
            connected_rail = rails_model.findRailData(connectedRailId)
            if connected_rail:
                connected_rail._markers.updateStatesLocally()

    def updateStatesLocally(self):
        def at_proximity(marker1, marker2):
            return abs(marker1.distance - marker2.distance) == 1

        def taken_marker_at_proximity(markers, marker):
            return any(m.taken for m in markers if at_proximity(marker, m))

        def connected_rail_from_marker(connectors, marker):
            return connectors.getByName(marker.connector).connectedRailId

        # for all markers
        for marker in self._items:
            overlapping = False
            if marker.at_boundary():
                connectedRailId = connected_rail_from_marker(self._connectors, marker)

                # at a shared boundary the lower id rail owns the tie
                if not marker.taken:
                    overlapping = connectedRailId != State.NotConnected and connectedRailId < self.rail.id

            # a taken marker only changes when its color changes
            if marker.taken:
                continue

            # blocked by a taken marker on this rail or across a connected boundary
            new_state = MarkerState.Blocked if overlapping else MarkerState.Free
            if taken_marker_at_proximity(self._items, marker):
                new_state = MarkerState.Blocked
            if self.takenAcrossBoundary(marker):
                new_state = MarkerState.Blocked
            marker.state = new_state

    def connectedRailIds(self):
        ids = []
        for connector in self._connectors._items:
            if connector.connected() and connector.connectedRailId not in ids:
                ids.append(connector.connectedRailId)
        return ids

    def boundaryMarkerTo(self, railId):
        for marker in self._items:
            if marker.at_boundary():
                connector = self._connectors.getByName(marker.connector)
                if connector.connectedRailId == railId:
                    return marker
        return None

    def takenAcrossBoundary(self, marker):
        rails_model = self.rail.parent()

        for boundary in self._items:
            if not boundary.at_boundary():
                continue

            # only the boundary marker or its immediate neighbour can overlap
            local_gap = abs(marker.distance - boundary.distance)
            if local_gap > 1 or not self.path_ids_compatible(marker.path_id, boundary.path_id):
                continue

            connectedRailId = self._connectors.getByName(boundary.connector).connectedRailId
            if connectedRailId == State.NotConnected:
                continue

            connected_rail = rails_model.findRailData(connectedRailId)
            if connected_rail is None:
                continue

            remote = connected_rail._markers
            remote_boundary = remote.boundaryMarkerTo(self.rail.id)
            if remote_boundary is None:
                continue

            # taken marker across the junction: block when the combined gap is <= 1 stud
            for taken in remote._items:
                if not taken.taken:
                    continue
                if not remote.path_ids_compatible(taken.path_id, remote_boundary.path_id):
                    continue
                if local_gap + abs(taken.distance - remote_boundary.distance) <= 1:
                    return True

        return False

    @Slot(result=int)
    def activeCount(self, path_id = None):
        if path_id == None:
            return sum(1 for item in self._items if item.taken)
        else:
            return sum(1 for item in self._items if item.taken and item.path_id in (None, "", path_id))
