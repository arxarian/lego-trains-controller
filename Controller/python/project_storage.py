# This Python file uses the following encoding: utf-8

import json
from pathlib import Path

from PySide6.QtCore import QObject, Slot, Property, Signal

from project import Project

class ProjectStorage(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.projects = []
        self.base_path = Path("projects")   # TODO - is it used?
        self.base_path.mkdir(parents=True, exist_ok=True)
        self._currentProject = Project("rails", parent=self)  # a default projet name for now

    def currentProject(self):
        return self._currentProject

    def set_currentProject(self, value):
        self._currentProject = value
        self.currentProject_changed.emit()

    currentProject_changed = Signal()
    currentProject = Property(str, currentProject, set_currentProject, notify=currentProject_changed)

    @Slot(str)
    def loadProject(self, name: str) -> Project:
        file = Path(name + ".json")

        if not file.exists():
            raise FileNotFoundError(f"Project '{name}' not found")

        with file.open("r", encoding="utf-8") as f:
            data = json.load(f)
            self.set_currentProject(Project(name, data, self))
            print("project loaded")

    @Slot(QObject)
    def saveProject(self, project: Project):
        data = project.data()

        with project.path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print("project saved")

    @Slot()
    def listProjects(self):
        print("TODO - not implemented")
        return ["karl", "marx"]
