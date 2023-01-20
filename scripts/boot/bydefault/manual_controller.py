import asyncio
import websockets
import websockets.client
import logging

from getch import getch
from typing import Union, Tuple

from protocol import *
from geometry import TraingleKinematic, normalized_rect
from calib_gallery import *

logging.basicConfig(level=logging.INFO)

async def console_input_loop(mpos: Tuple[float, float], ws: websockets.client.WebSocketClientProtocol):
    loop = asyncio.get_event_loop()

    async def agetch():
        return await loop.run_in_executor(None, getch)

    ARROW_STEP = 0.5
    CART_STEP = 0.1

    N = 0
    points = []

    normalized_rect = [(0, 10), (430, -10), (420, -350), (0, -295)]
    kinematic = TraingleKinematic(CALIB, normalized_rect)

    while True:
        esc = ord(await agetch())
        if esc == 27:
            if ord(await agetch()) == 91:
                key = ord(await agetch())
                move = [0, 0]

                #if key == 65:  # Up arrow key
                #    move[0] += ARROW_STEP
                #    move[1] += ARROW_STEP
                #elif key == 66:  # Down arrow key
                #    move[0] -= ARROW_STEP
                #    move[1] -= ARROW_STEP
                #elif key == 67:  # Right arrow key
                #    move[0] -= ARROW_STEP
                #    move[1] += ARROW_STEP
                #elif key == 68:  # Left arrow key
                #    move[0] += ARROW_STEP
                #    move[1] -= ARROW_STEP
                #mpos = (mpos[0] + move[0], mpos[1] + move[1])
                #await ws.send(MoveCommand(mpos[0], mpos[1]).serialize())
                #logging.debug(f'Response from server: {await ws.recv()}')

                if key == 65:  # Up arrow key
                    move[1] -= CART_STEP
                elif key == 66:  # Down arrow key
                    move[1] += CART_STEP
                elif key == 67:  # Right arrow key
                    move[0] += CART_STEP
                elif key == 68:  # Left arrow key
                    move[0] -= CART_STEP

                mpos = kinematic.pos 
                mpos = (mpos[0] + move[0], mpos[1] + move[1])
                logging.info(f'Pos: {mpos}')
                mpos = kinematic.get_move(mpos)
                await ws.send(MoveCommand(mpos[0], mpos[1]).serialize())
                response = await ws.recv()
                logging.debug(f'Response from server: {response}')
        elif esc == ord('h'):
            await ws.send(HomeCommand().serialize())
            response = await ws.recv()
            logging.debug(f'Response from server: {response}')
        elif esc == ord('z'):
            #mpos = (125.22000000000014, 422.432)
            mpos = kinematic.get_move_normalized((0.5, 0))
            await ws.send(MoveCommand(mpos[0], mpos[1]).serialize())
            response = await ws.recv()
            logging.debug(f'Response from server: {response}')
        elif esc == ord('1'):
            CART_STEP = 0.1
            logging.info(f"step: {CART_STEP}")
        elif esc == ord('2'):
            CART_STEP = 0.5
            logging.info(f"step: {CART_STEP}")
        elif esc == ord('3'):
            CART_STEP = 1
            logging.info(f"step: {CART_STEP}")
        elif esc == ord('4'):
            CART_STEP = 5
            logging.info(f"step: {CART_STEP}")
        elif esc == ord('5'):
            CART_STEP = 10
            logging.info(f"step: {CART_STEP}")
        elif esc == ord('6'):
            CART_STEP = 20
            logging.info(f"step: {CART_STEP}")
        elif esc == ord('q'):
            break

        elif esc == ord('w'):
            await ws.send(WaitCommand().serialize())
            response = await ws.recv()
            print(f'Wait result: {response}')

async def client_loop():
    while True:
        try:
            async with websockets.connect(f'ws://luysy-imn-eh.local:{MOTION_SERVER_PORT}') as ws:
                logging.info(f'Connected to motion server at localhost:{MOTION_SERVER_PORT}')

                await ws.send(WaitCommand().serialize())
                pos_msg = json.loads(await ws.recv())
                pos = (float(pos_msg['x']), float(pos_msg['y']))

                logging.info(f'Starting position: {pos}')

                await console_input_loop(pos, ws)

        except Exception as ex:
            logging.error(f'Error: {ex}, reconnecting...')
            await asyncio.sleep(1)    

loop = asyncio.get_event_loop()
loop.run_until_complete(client_loop())