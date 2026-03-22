# This Python file uses the following encoding: utf-8

from PySide6.QtCore import QObject, Slot

import re

class Planner(QObject):
    def __init__(self, rails, network, parent=None):
        super().__init__(parent)
        self._rails = rails
        self._network = network

    def updateRailsModel(self, rails):
            self._rails = rails

    @Slot(str)
    def reserve(self, segment_id):
        self._network.reserve(segment_id)

    @Slot(str)
    def unreserve(self, segment_id):
        self._network.unreserve(segment_id)

    @Slot(str)  # TODO - debug function more or less
    def plan(self, paths):
        paths = paths.split(",")
        planned_paths = {}
        for path in paths:
            match = re.match(r"(\d+)(.*)", path)
            if match:
                rail_id = int(match.group(1))
                path_id = match.group(2)
                planned_paths[rail_id] = path_id

        for rail in self._rails.items():
            path = planned_paths.get(rail.id, "None")
            rail._path_indicators.set_path_id_active(path)


