from __future__ import annotations

from PySide6.QtCore import Slot, QModelIndex
from PySide6.QtQml import QmlElement
from PySide6.QtGui import QColor

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
        self.rail = None
        print("self._data", self._data)

    def resolveColor(self, index):
        color = next((d["color"] for d in self._data if d["index"] == index), None)
        return None if color is None else QColor(color)

    def setModel(self, metaData):
        self.beginInsertRows(QModelIndex(), 0, len(metaData) - 1)
        for i, d in enumerate(metaData):
            self._items.append(Marker(data=d, index=i, color=self.resolveColor(i) , parent=self))
        self.endInsertRows()
        self._data = [] # clear the original data, not needed anymore

        self.updateStates()

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

    def getConnectionDisabledDistances(self):
        if not self.rail:
            return set()

        disabled = set()
        conn_to_distance = {}

        for path in self.rail._paths:
            from_conn = next((c for c in self.rail._connectors._items if c._name == path["from"]), None)
            if from_conn and from_conn._dir == "forward":
                conn_to_distance[path["from"]] = 0
                conn_to_distance[path["to"]] = path["length"]

        for connector in self.rail._connectors._items:
            if connector.connected() and self.rail._id > connector._connectedRailId:
                distance = conn_to_distance.get(connector._name)
                if distance is not None:
                    disabled.add(distance)

        return disabled

    def getCrossRailBlockedIndices(self, connectedRail):
        if connectedRail is None:
            return

    # TODO - move it to marker itself, use real value instead of 0 and 16
    def atBoundary(self, marker):
        return (marker.distance == 16 or marker.distance == 0)

    def atProximity(self, marker1, marker2):
        return abs(marker1.distance - marker2.distance) == 1 # + add from connected if at boundary

    # called first for self and third for connected by updateConnectedRailsEnabledStates()
    def updateStates(self, connectedRail = None):
        print("updateStates", self)
        #free_markers = [m for m in self._items if m.visible]

        # for all markers
        for marker in self._items:
            print("marker", marker.distance, "state", marker.state)
            if marker.taken:
                continue

            new_state = MarkerState.Free
            for proximity_marker in self._items:
                if self.atProximity(marker, proximity_marker) and proximity_marker.taken:
                    new_state = MarkerState.Blocked
            marker.state = new_state


            #marker.set_state(marker.state == MarkerState. and not self.atProximity(marker))

            #if marker.visible:
            #    continue
        #    blocked = any(
        #        abs(v.distance - marker.distance) == 1
        #        and self._path_ids_compatible(marker.path_id, v.path_id)
        #        for v in free_markers
        #    )

        #    # TODO - here return connected marker!
        #    connected_marker = False#marker.distance == 16 or marker.distance == 0

        #    at_connection = False#marker.distance in disabled_at_connection
        #    marker.set_enabled(not at_connection)
        #    marker.set_enabled(not blocked and not connected_marker and not at_connection)

    ## called second for self
    #def updateConnectedRailsEnabledStates(self):
    #    if not self.rail:
    #        return

    #    rails_model = self.rail.parent()
    #    for connector in self.rail._connectors._items:
    #        if connector.connected():
    #            connected_rail = rails_model.findRailData(connector._connectedRailId)
    #            if connected_rail:
    #                print("original", self.rail.id, "connected", connected_rail.id)
    #                connected_rail._markers.updateEnabledStates(self.rail)

    @Slot(result=int)
    def activeCount(self, path_id = None):
        if path_id == None:
            return sum(1 for item in self._items if item.taken)
        else:
            return sum(1 for item in self._items if item.taken and item.path_id in (None, "", path_id))
