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

import random

import subprocess

logging.basicConfig(level=logging.INFO)

def nsin(x):
    return sin(x) * 0.5 + 0.5

from luysy_svg import get_files

data = get_files()

# data = [x for x in data if x[0] == "chr"]

print(data)

LED_TIME = 5 * 60
EVN_TIME = 2 * 60

fragments = {
    "led": [(-120, 433), (600, 434), (620, -520), (-320, -306)],
    "chr": [(5, 30), (430, 1), (425, -323), (-4, -272)],
    "primorka": [(-280, -30), (-60, -41), (-63, -188), (-283, -178)],
    "piskarevka": [(467, -128), (626, -128), (623, -252), (467, -256)],
    "strelka": [(2, 261), (215, 257), (216, 113), (2, 123)],
    "damba": [(-253, 248), (-78, 248), (-78, 103), (-258, 108)],
    "center": [(269, 383), (382, 378), (384, 237), (270, 237)],
    "ohta": [(443, 303), (599, 298), (596, 84), (441, 89)],
    "evn": [(1100, 620), (1740, 620), (1900, -240), (1130, -260)]
}

async def go_led(ws: websockets.client.WebSocketClientProtocol):
    last_time = time()

    subprocess.run(["xdotool", "key", "2"])

    while True:
        t = time()

        route = random.choice(data)

        logging.info(f'route: {route[2]}')

        if route[0] not in fragments:
            continue

        kinematic = TraingleKinematic(CALIB, fragments[route[0]])

        for i, point in enumerate(route[1]):
            if i % 10 != 0:
                continue

            mpos = kinematic.get_move_normalized((point[0], 1-point[1]))

            # logging.info(f'go to mpos {mpos}')

            await ws.send(MoveCommand(mpos[0], mpos[1]).serialize())
            response = await ws.recv()
            logging.debug(f'Response from server: {response}')

        if t - last_time > LED_TIME:
            await ws.send(WaitCommand().serialize())
            await ws.recv()
            return

async def go_evn(ws: websockets.client.WebSocketClientProtocol):
    last_time = time()

    subprocess.run(["xdotool", "key", "1"])

    phases_x = [0] * 5
    freqs_x = [1, 2, 3, 4, 5]
    phases_y = [0] * 5
    freqs_y = [1, 2, 3, 4, 5]

    kinematic = TraingleKinematic(CALIB, fragments["evn"])

    while True:
        t = time()

        x = sum([nsin(f * t / 5 + p) for f, p in zip(freqs_x, phases_x)]) / len(phases_x)
        y = sum([nsin(f * t / 5 + p) for f, p in zip(freqs_y, phases_y)]) / len(phases_y)

        logging.info(f'raw: {x} {y}')

        phases_x = [a + (random.random() - 0.5) * 0.1 for a in phases_x]
        phases_y = [a + (random.random() - 0.5) * 0.1 for a in phases_y]

        mpos = kinematic.get_move_normalized((x, y))

        # logging.info(f'go to mpos {mpos}')

        await ws.send(MoveCommand(mpos[0], mpos[1]).serialize())
        response = await ws.recv()
        logging.debug(f'Response from server: {response}')

        if t - last_time > EVN_TIME:
            await ws.send(WaitCommand().serialize())
            await ws.recv()
            return



async def main_loop(mpos: Tuple[float, float], ws: websockets.client.WebSocketClientProtocol):
    loop = asyncio.get_event_loop()


    
    while True:
        await go_led(ws)
        await go_evn(ws)

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