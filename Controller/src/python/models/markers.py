from __future__ import annotations

from PySide6.QtCore import Slot, QModelIndex
from PySide6.QtQml import QmlElement
from PySide6.QtGui import QColor

from python.items.connector import State
from python.items.marker import Marker, MarkerState
from python.models.object_based_model import ObjectBasedModel

#import datetime

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

        print("updateStates", self.rail.id)

        connections = []

        # for all markers
        for marker in self._items:
            overlapping = False
            print("marker", marker.distance)
            if marker.at_boundary():
                connectedRailId = connected_rail_from_marker(self._connectors, marker)
                if connectedRailId != State.NotConnected:
                    connections.append((connectedRailId, marker))

                # if at boundary and connected, resolved overlapping markers
                if not marker.taken:
                    overlapping = connectedRailId != State.NotConnected and connectedRailId < self.rail.id

            # taken marker is updated only of color changes -> continue
            if marker.taken:
                continue

            # if there is a taken marker at proximity, blocked this one, otherwise free
            new_state = MarkerState.Blocked if overlapping else MarkerState.Free
            if taken_marker_at_proximity(self._items, marker):
                new_state = MarkerState.Blocked
            marker.state = new_state

        print("loop connected", connections)
        # find all markers at proximity
        # if they have an equivalent, block equivalent

        rails_model = self.rail.parent() # TODO - fix parent of parent...
        for rail_id, marker in connections:
            connected_rail = rails_model.findRailData(rail_id)
            for marker in connected_rail._markers._items:
                if marker.at_boundary():
                    print("close marker", marker.distance)



            ## if two rails are connected, the one with lower id has blocked boundary marker point
            #if marker.at_boundary():
            #    #print("marker.connector", marker.connector, self._connectors)
            #    connectedRailId = connected_rail_from_marker(self._connectors, marker)
            #    print(self.rail.id, "connected to", connectedRailId)

            #    if connectedRailId == State.NotConnected:
            #        print("non connected, continue")
            #        continue

            #    if not marker.taken:
            #        marker.state = MarkerState.Blocked if connectedRailId > self.rail.id else MarkerState.Free
            #        print("not taken", marker.state)

            #    # no need to go further if blocked
            #    if marker.blocked:
            #        print("blocked, continue")
            #        continue

            #    # I need the overlapping marker from the connected rail
            #    rails_model = self.rail.parent() # TODO - fix parent of parent...
            #    connected_rail = rails_model.findRailData(connectedRailId)
            #    close_markers = connected_rail._markers._items
            #    close_connectors = connected_rail._connectors
            #    print("connected_rail", connected_rail.id)

            #    # loop markers at boundary and compare if that marker reference a connector connected to this rail
            #    for close_marker in connected_rail._markers._items:
            #         # TODO - fix for marker 1 and 15 (not at boundary) ?????
            #        if close_marker.at_boundary():
            #            for proximity_marker in connected_rail._markers._items:
            #                if atProximity(proximity_marker, close_marker):
            #                    print("close_marker", close_marker.distance, connected_rail_from_marker(close_connectors, close_marker),
            #                    self.rail.id, connected_rail_from_marker(self._connectors, marker))
            #                    if connected_rail_from_marker(close_connectors, close_marker) == self.rail.id:
            #                        print("got it!")
            #                        if taken_marker_at_proximity(close_markers, close_marker):
            #                             marker.state = MarkerState.Blocked
            #                             break

                #print("connected_rail", connector._connectedRailId)#, connected_rail._markers)
                # check if at proximity
                # and set the state accordingly

                ## THE LAST THING - Blocked if connected rails is TAKEN
                ## I got connectedRailId, I need to get the rail
                #rails_model = self.rail.parent() # TODO - fix parent of parent...
                #connected_rail = rails_model.findRailData(connector._connectedRailId)
                #print("connected_rail", connector._connectedRailId)#, connected_rail._markers)
                ## I need to search the markers of that rail to find, which one is connected to this rail
                #for close_marker in connected_rail._markers._items:
                #    print("close marker", close_marker.distance, "at_boundary", close_marker.at_boundary(), "taken", close_marker.taken)
                #    if close_marker.at_boundary() and close_marker.taken:
                #        close_connector = connected_rail._connectors.getByName(close_marker.connector)
                #        if close_connector.connectedRailId == self.rail.id:
                #           marker.state = MarkerState.Blocked

                # when I have it, I just check of taken


                #for connector in self.rail._connectors._items:
                #    if connector.connected():
                #        rails_model = self.rail.parent()
                #        siblings = rails_model.findsiblingsOf(connector._connectedRailId)
                #        print(datetime.datetime.now().time(), "siblings of", self.rail.id, "are", siblings, self.rail.id in siblings)
                #        #print(datetime.datetime.now().time(), "connector._connectedRailId", connector._connectedRailId)
                #        #marker.state = MarkerState.Blocked


                #rails_model = self.rail.parent()
                #for connector in self.rail._connectors._items:
                #    if connector.connected():
                #        connected_rail = rails_model.findRailData(connector._connectedRailId)
                #        if connected_rail:
                #            print("original", self.rail.id, "connected", connected_rail.id)
                #            connected_rail._markers.updateEnabledStates(self.rail)



    @Slot(result=int)
    def activeCount(self, path_id = None):
        if path_id == None:
            return sum(1 for item in self._items if item.taken)
        else:
            return sum(1 for item in self._items if item.taken and item.path_id in (None, "", path_id))
