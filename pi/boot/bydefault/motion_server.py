import asyncio
import websockets
import logger

from protocol import *

async def server_loop(ws):
    try:
        async for msg in ws:
            print(msg)
    except Exception as ex:
        logger.info(f'Client session error: {ex}')
        raise       

async def main():
    async with websockets.serve(server_loop, 'localhost', MOTION_SERVER_PORT):
        await asyncio.Future()

asyncio.run(main())