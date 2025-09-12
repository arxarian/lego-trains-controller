# This Python file uses the following encoding: utf-8

import json
from pathlib import Path

from project import Project

class ProjectStorage:
    def __init__(self):
        self.projects = {}
        self.base_path = Path("projects")
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.currentProject = Project()

    def loadProject(self, name: str) -> Project:
        file = self.project_file(name + ".json")

        if not file.exists():
            raise FileNotFoundError(f"Project '{name}' not found")

        with file.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return Project(name, data)

    def saveProject(self, project: Project):
        data = project.data()

        with project.path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def listProjects(self):
        print("TODO - not implemented")
        return ["karl", "marx"]
