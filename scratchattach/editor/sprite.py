from . import base, project


class Sprite(base.ProjectSubcomponent):
    def __init__(self, _project: project.Project=None):
        super().__init__(_project)

    @staticmethod
    def from_json(data: dict):
        pass

    def to_json(self) -> dict:
        pass