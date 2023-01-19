import asyncio
import websockets
import websockets.client
import logging

from getch import getch
from typing import Union, Tuple

from protocol import *
from geometry import TraingleKinematic, normalized_rect
from calib_gallery import *

from math import sin
from time import time

logging.basicConfig(level=logging.INFO)

def nsin(x):
    return sin(x) * 0.5 + 0.5

async def main_loop(mpos: Tuple[float, float], ws: websockets.client.WebSocketClientProtocol):
    loop = asyncio.get_event_loop()

    normalized_rect = [(0, 10), (430, -10), (420, -350), (0, -295)]
    kinematic = TraingleKinematic(CALIB, normalized_rect)

    while True:
        t = time()
        mpos = kinematic.get_move_normalized((nsin(t), nsin(t * 2)))
        await ws.send(MoveCommand(mpos[0], mpos[1]).serialize())
        logging.debug(f'Response from server: {await ws.recv()}')

async def client_loop():
    while True:
        try:
            async with websockets.connect(f'ws://localhost:{MOTION_SERVER_PORT}') as ws:
                logging.info(f'Connected to motion server at localhost:{MOTION_SERVER_PORT}')

                await ws.send(WaitCommand().serialize())
                pos_msg = json.loads(await ws.recv())
                pos = (float(pos_msg['x']), float(pos_msg['y']))

                logging.info(f'Starting position: {pos}')

                await main_loop(pos, ws)

        except Exception as ex:
            logging.error(f'Error: {ex}, reconnecting...')
            await asyncio.sleep(1)    

asyncio.run(client_loop())