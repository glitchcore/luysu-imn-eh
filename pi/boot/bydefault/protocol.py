from typing import Union

MOTION_SERVER_PORT=13337

class MoveCommand:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __str__(self) -> str:
        return f'move {self.x} {self.y}'

class ResetCommand:
    pass

class HomeCommand:
    pass

AnyCommand = Union[MoveCommand, ResetCommand, HomeCommand]

def command_from_json(o: dict) -> AnyCommand:
    cmd = o['cmd']
    if cmd == 'move':
        return MoveCommand(float(o['x']), float(o['y']))
    elif cmd == 'reset':
        return ResetCommand()
    elif cmd == 'home':
        return HomeCommand()

    raise RuntimeError(f'Unexpected command: {cmd}')

def command_to_json(cmd: AnyCommand):
    if isinstance(cmd, MoveCommand):
        return {'cmd': 'move', 'x': cmd.x, 'y': cmd.y}
    elif isinstance(cmd, ResetCommand):
        return {'cmd': 'reset'}
    elif isinstance(cmd, HomeCommand):
        return {'cmd': 'home'}

    raise RuntimeError(f'Unexpected command: {cmd}')