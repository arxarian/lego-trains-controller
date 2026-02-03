# This Python file uses the following encoding: utf-8

from PySide6.QtCore import QObject, Slot

import re

class Planner(QObject):
    def __init__(self, rails, parent=None):
        super().__init__(parent)
        self._rails = rails

    def updateRailsModel(self, rails):
            self._rails = rails

    @Slot(str)
    def updatePaths(self, paths):
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


