import asyncio
import aioconsole
import websockets
import logger

from typing import Union

from protocol import *

async def process_input():
    ARROW_STEP = 0.5

    prefix = await aioconsole.input("Please input the prefix of the file name: ")
    N = 0
    points = []

    esc = ord(await aioconsole.getch())
    if esc == 27:
        if ord(await aioconsole.getch()) == 91:
            key = ord(getch())
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

            controller.wait_run(f"G1F1000X{controller.device.mpos[0] + move[0]}Y{controller.device.mpos[1] + move[1]}")
    elif esc == 32:
        points.append(d.mpos)
    elif esc == 13:
        with open(f"{prefix}-{N}.dat", "w") as f:
            for point in points:
                f.write(f"{point[0]},{point[1]}\n")
        N += 1
        points.clear()
    elif esc == ord('p'):
        prefix = input("Please input the prefix of the file name: ")
        N = 0
    elif esc == ord('q'):
        quit()

async def client_loop(ws):
    while True:
        try:
            async with websockets.connect(f'ws://localhost:{MOTION_SERVER_PORT}') as ws:
                logger.info(f'Connected to motion server at localhost:{MOTION_SERVER_PORT}')

                while True:
                    cmd = await read_command()
                
        except Exception as ex:
            logger.error(f'Error: {ex}, reconnecting...')    

async def main():
    async with websockets.serve(server_loop, 'localhost', MOTION_SERVER_PORT):
        await asyncio.Future()

asyncio.run(main())