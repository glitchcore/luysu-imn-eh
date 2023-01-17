import asyncio
import websockets
import logging

from protocol import *

async def server_loop(ws):
    try:
        await ws.send('{"x": 0, "y": 0}')
        async for msg in ws:
            print(msg)
    except Exception as ex:
        logging.info(f'Client session error: {ex}')
        raise       

async def main():
    async with websockets.serve(server_loop, 'localhost', MOTION_SERVER_PORT):
        await asyncio.Future()

asyncio.run(main())