import json
from typing import Union, Optional

MOTION_SERVER_PORT=13337

class MoveCommand:
    NAME='move'
    def __init__(self, x: Optional[float], y: Optional[float]):
        self.x = x
        self.y = y

    def to_json(self) -> dict:
        return {'cmd': self.NAME, 'x': self.x, 'y': self.y}

    def serialize(self) -> str:
        return json.dumps(self.to_json())

    def __str__(self) -> str:
        return f'move {self.x} {self.y}'

class WaitCommand:
    NAME='wait'
    def __init__(self):
        pass

    def to_json(self) -> dict:
        return {'cmd': self.NAME}

    def serialize(self) -> str:
        return json.dumps(self.to_json())

class HomeCommand:
    NAME='home'
    def __init__(self):
        pass

    def to_json(self) -> dict:
        return {'cmd': self.NAME}

    def serialize(self) -> str:
        return json.dumps(self.to_json())

AnyCommand = Union[MoveCommand, WaitCommand, HomeCommand]

class StatusResponse:
    def __init__(self, status: str, x: Optional[float] = None, y: Optional[float] = None):
        self.status = status
        self.x = x
        self.y = y

    def to_json(self) -> dict:
        return {'status': self.status, 'x': self.x, 'y': self.y}

    def serialize(self) -> str:
        return json.dumps(self.to_json())

    def __str__(self):
        return self.serialize()