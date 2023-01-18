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

async def motion_controller_loop(controller: AsyncMotionController, commands: asyncio.Queue, results: asyncio.Queue):
    seq = None
    while True:
        try:
            try:
                await controller.wait_run("")
            except Device.DeviceNeedResetError:
                await controller.reset_retract()

            #await controller.homing()

            if seq is not None:
                x,y = await controller.pos()
                await results.put((seq, StatusResponse('ok', x, y)))
                    
                
            while True:
                nseq, cmd = await commands.get()
                seq = nseq

                if isinstance(cmd, MoveCommand):
                    status = await controller.move_async(cmd.x, cmd.y)
                    await results.put((seq, StatusResponse(status)))
                elif isinstance(cmd, WaitCommand):
                    x, y = await controller.wait_run("")
                    await results.put((seq, StatusResponse('ok', x, y)))
                elif isinstance(cmd, HomeCommand):
                    await controller.homing()
                    await results.put((seq, StatusResponse('ok')))
                else:
                    logging.info(f'Unexpected command: {cmd}')
                    await results.put((seq, StatusResponse('error')))
        
        except Device.DeviceMalfunction as e:
            logging.info(f"Device malfunction: {e}. Back to home")
            await controller.reset_retract()

CONNECTION_SEQ = 0
DEVICE_LOCK = asyncio.Lock()

async def server_loop(commands: asyncio.Queue, results: asyncio.Queue, ws):
    global CONNECTION_SEQ
    global DEVICE_LOCK

    try:
        if DEVICE_LOCK.locked():
            raise RuntimeError('Parallel session detected')

        async with DEVICE_LOCK:
            CONNECTION_SEQ += 1
            seq = CONNECTION_SEQ

            async for msg in ws:
                cmd_obj = json.loads(msg)
                cmd_name = cmd_obj['cmd']

                if cmd_name == 'move':
                    x = None
                    y = None

                    if 'x' in cmd_obj:
                        x = float(cmd_obj['x'])
                    if 'y' in cmd_obj:
                        y = float(cmd_obj['y'])
                    
                    await commands.put((seq, MoveCommand(x, y)))
                elif cmd_name == 'wait':
                    await commands.put((seq, WaitCommand()))
                elif cmd_name == 'home':
                    await commands.put((seq, HomeCommand()))
                else:
                    raise ValueError(f'Unexpected command: {cmd_obj}')

                while True:
                    nseq, result = await results.get()
                    if nseq != seq:
                        logging.info('Stale result status: {result} with seq {nseq}, current seq: {seq}; discarding')
                    else:
                        await ws.send(result.serialize())
                        break

    except Exception as ex:
        logging.info(f'Client session error: {ex}')
        raise      

async def main():
    d = Device("/dev/serial/by-id/usb-1a86_USB2.0-Ser_-if00-port0", 115200)
    await post(lambda: d.reset())
    logging.info("Device reset successfully")

    commands = asyncio.Queue(maxsize=30)
    results = asyncio.Queue(maxsize=30)

    sync_controller = MotionController(d)
    controller = AsyncMotionController(sync_controller)

    mc_loop = motion_controller_loop(controller, commands, results)

    async with websockets.serve(lambda ws: server_loop(commands, results, ws), 'localhost', MOTION_SERVER_PORT):
        await mc_loop

asyncio.run(main())