import asyncio
import websockets
import websockets.client
import logging

from getch import getch
from typing import Union, Tuple

from protocol import *

async def console_input_loop(mpos: Tuple[float, float], ws: websockets.client.WebSocketClientProtocol):
    loop = asyncio.get_event_loop()

    async def agetch():
        return await loop.run_in_executor(None, getch)

    ARROW_STEP = 0.5

    prefix = await loop.run_in_executor(None, input, "Please input the prefix of the file name: ")
    
    N = 0
    points = []

    while True:
        esc = ord(await agetch())
        if esc == 27:
            if ord(await agetch()) == 91:
                key = ord(await agetch())
                move = [0, 0]

                if key == 65:  # Up arrow key
                    move[0] += ARROW_STEP
                    move[1] += ARROW_STEP
                elif key == 66:  # Down arrow key
                    move[0] -= ARROW_STEP
                    move[1] -= ARROW_STEP
                elif key == 67:  # Right arrow key
                    move[0] -= ARROW_STEP
                    move[1] += ARROW_STEP
                elif key == 68:  # Left arrow key
                    move[0] += ARROW_STEP
                    move[1] -= ARROW_STEP

                mpos = (mpos[0] + move[0], mpos[1] + move[1])
                await ws.send(MoveCommand(mpos[0], mpos[1]).serialize())
                logging.debug(f'Response from server: {await ws.recv()}')
        elif esc == 32:
            points.append(mpos)
        elif esc == 13:
            with open(f"{prefix}-{N}.dat", "w") as f:
                for point in points:
                    f.write(f"{point[0]},{point[1]}\n")
            N += 1
            points.clear()
        elif esc == ord('p'):
            prefix = await loop.in_executor(None, input, "Please input the prefix of the file name: ")
            N = 0
        elif esc == ord('q'):
            quit()

async def client_loop():
    while True:
        try:
            async with websockets.connect(f'ws://localhost:{MOTION_SERVER_PORT}') as ws:
                logging.info(f'Connected to motion server at localhost:{MOTION_SERVER_PORT}')

                pos_msg = json.loads(await ws.recv())
                pos = (float(pos_msg['x']), float(pos_msg['y']))

                logging.info(f'Starting position: {pos}')

                await console_input_loop(pos, ws)
                
        except Exception as ex:
            logging.error(f'Error: {ex}, reconnecting...')    

asyncio.run(client_loop())