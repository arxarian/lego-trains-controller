# This Python file uses the following encoding: utf-8

import json
from pathlib import Path

from PySide6.QtCore import QObject, Slot, Property, Signal

from project import Project

DEFAULT_NAME="rails"      # a default projet name for now

class ProjectStorage(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.projects = []
        self.base_path = Path("projects")
        self.base_path.mkdir(parents=True, exist_ok=True)
        self._currentProject = Project(DEFAULT_NAME, parent=self)

    def currentProject(self):
        return self._currentProject

    def set_currentProject(self, value):
        self._currentProject = value
        self.currentProject_changed.emit()

    currentProject_changed = Signal()
    currentProject = Property(str, currentProject, set_currentProject, notify=currentProject_changed)

    @Slot(str)
    def loadProject(self, name: str) -> Project:
        if name == str():
            print("no project name provided")
            return

        file = self.base_path.joinpath(name + ".json")

        if not file.exists():
            raise FileNotFoundError(f"Project '{name}' not found")

        with file.open("r", encoding="utf-8") as f:
            data = json.load(f)
            self.set_currentProject(Project(name, data, self))
            print("project loaded")

    @Slot(QObject)
    def saveProject(self, project: Project):
        data = project.data()

        path = self.base_path.joinpath(project.name + ".json")
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print("project saved")

    @Slot(result=list)
    def listProjects(self):
        return [path.__str__() for path in list(self.base_path.glob("*.json"))]
