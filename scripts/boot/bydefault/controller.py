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

from luysy_svg import get_files

data = get_files()

LED_TIME = 5 * 60
EVN_TIME = 2 * 60

fragments = {
    "led": [],
    "chr": [(0, 10), (430, -10), (420, -350), (0, -295)]
}

async def main_loop(mpos: Tuple[float, float], ws: websockets.client.WebSocketClientProtocol):
    loop = asyncio.get_event_loop()

    kinematic = TraingleKinematic(CALIB, fragments["chr"])

    last_time = time()

    phases_x = [0] * 5
    freqs_x = [1, 2, 3, 4, 5]
    phases_y = [0] * 5
    freqs_y = [1, 2, 3, 4, 5]

    while True:
        t = time()

        if t - last_time > LED_TIME:
            logging.info(f'go to evn')

        x = sum([nsin(f * t / 20 + p) for f, p in zip(freqs_x, phases_x)]) / len(phases_x)
        y = sum([nsin(f * t / 20 + p) for f, p in zip(freqs_y, phases_y)])

        phases_x = [a + (random.random() - 0.5) * 0.1 for a in phases_x]
        phases_y = [a + (random.random() - 0.5) * 0.1 for a in phases_y]

        mpos = kinematic.get_move_normalized((x, y))
        await ws.send(MoveCommand(mpos[0], mpos[1]).serialize())
        response = await ws.recv()
        logging.debug(f'Response from server: {response}')

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

loop = asyncio.get_event_loop()
loop.run_until_complete(client_loop())