import json
from typing import Union, Optional

MOTION_SERVER_PORT=13337

class MoveCommand:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def to_json(self) -> dict:
        return {'cmd': 'move', 'x': self.x, 'y': self.y}

    def serialize(self) -> str:
        return json.dumps(self.to_json())

    def __str__(self) -> str:
        return f'move {self.x} {self.y}'

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