import asyncio
import websockets
import logging

from protocol import *
from motion_controller import MotionController
from device import Device

logging.basicConfig(level=logging.DEBUG)

async def post(*args):
    return await asyncio.get_event_loop().run_in_executor(None, *args)

class AsyncMotionController:
    def __init__(self, controller: MotionController):
        self.controller = controller
        self.lock = asyncio.Lock()

    async def try_lock(self):
        return await asyncio.wait_for(self.lock.acquire(), 0.1)

    async def reset_retract(self):
        return await post(MotionController.reset_retract, self.controller) 

    async def homing(self):
        return await post(MotionController.homing, self.controller)

    async def move(self, x: Optional[float], y: Optional[float], speed:Optional[float] = None):
        return await post(MotionController.move, self.controller, x, y, speed)

    async def move_async(self, x: Optional[float], y: Optional[float], speed: Optional[float] = None):
        return await post(MotionController.move_async, self.controller, x, y, speed)

    async def wait_run(self, cmd: str):
        return await post(MotionController.wait_run, self.controller, cmd)

    async def pos(self):
        return await post(lambda: self.controller.pos)

async def motion_controller_loop(controller: AsyncMotionController, clients: asyncio.Queue):
    client = None

    while True:
        try:
            try:
                await controller.wait_run("")
            except Device.DeviceNeedResetError:
                await controller.reset_retract()

            await controller.homing()

            while True:
                try:
                    if not client:
                        client = await clients.get()
                    x, y = await controller.pos()
                    await client.send(StatusResponse('ok', x, y).serialize())

                    async for msg in client:
                        msg_obj: dict = json.loads(msg)
                        cmd = msg_obj['cmd']

                        if cmd == 'move':
                            x = None
                            y = None
                            if 'x' in msg_obj:
                                x = float(msg_obj['x'])

                            if 'y' in msg_obj:
                                y = float(msg_obj['y'])

                            status = await controller.move_async(x, y)
                            await client.send(StatusResponse(status).serialize())
                        elif cmd == 'home':
                            await controller.homing()
                            x, y = await controller.pos()
                            await client.send(StatusResponse('ok', x, y).serialize())
                        elif cmd == 'wait':
                            x, y = await controller.wait_run('')
                            await client.send(StatusResponse('ok', x, y))
                        else:
                            raise ValueError(f'Unexpected request: {msg_obj}')

                except Device.DeviceMalfunction:
                    raise
                except Device.DeviceNeedResetError:
                    raise
                except Device.TimeoutError:
                    raise
                except Exception as e:
                    logging.info(f'Client error:{e}, aborting connection')
                    client = None

        except Device.DeviceMalfunction as e:
            logging.info(f"Device malfunction: {e}. Back to home")
            await controller.reset_retract()

async def server_loop(queue: asyncio.Queue, ws):
    try:
        queue.put_nowait(ws)
        await asyncio.Future()
    except Exception as ex:
        logging.info(f'Client session error: {ex}')
        raise      

async def main():
    d = Device("/dev/serial/by-id/usb-1a86_USB2.0-Ser_-if00-port0", 115200)
    await post(lambda: d.reset())
    logging.info("Device reset successfully")

    clients = asyncio.Queue(maxsize = 1)
    sync_controller = MotionController(d)
    controller = AsyncMotionController(sync_controller)

    mc_loop = motion_controller_loop(controller, clients)

    async with websockets.serve(lambda ws: server_loop(clients, ws), 'localhost', MOTION_SERVER_PORT):
        await mc_loop

asyncio.run(main())