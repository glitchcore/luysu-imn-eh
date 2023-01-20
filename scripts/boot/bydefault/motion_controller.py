import time
import logging
import threading

from device import Device

class MotionControllerParameters:
    def __init__(self):
        self.w = 550
        self.retract_length = 2
        self.y_init_retract = 10
        self.draw_speed = 800

class MotionController:
    def __init__(self, device: Device, param = MotionControllerParameters()):
        self.device = device
        self.param = param
        self.home = [0, 0]

    def reset_retract(self, ):
        d = self.device

        d.reset()
        d.command("$21=0")
        # d.command("$10=2")

        status, mpos = d.get_status()

        if status == "Alarm":
            d.command("$X")

        retraction_target = (mpos[0] + self.param.retract_length, mpos[1] + self.param.retract_length)

        while abs(d.mpos[0] - retraction_target[0]) > 0.01 or abs(d.mpos[1] - retraction_target[1]) > 0.01:
            d.command(f"G1F1000X{retraction_target[0]}Y{retraction_target[1]}")

            while True:
                status, mpos = d.get_status()
                logging.debug("status: %s", status)
                logging.debug("X: %s Y: %s", mpos[0], mpos[1])
                if status != "Run":
                    break
                time.sleep(0.5)

        d.command("$21=1")

    def disable_y(self):
        self.device.command("M08")
        self.device.command("M05")

    def enable_both(self):
        self.device.command("M09")
        self.device.command("M05")

    def check_status(self, status: str):
        if status == "Alarm":
            raise Device.DeviceNeedResetError("Alarm status")
    
    def wait_buffer_capacity(self):
        d = self.device
        while d.buffer_capacity < 2:
            status, _ = d.get_status()
            if status != "Run":
                break

    def run(self, command: str):
        d = self.device
        self.wait_buffer_capacity()
        ret = d.command(command)
        status, _ = d.get_status()
        self.check_status(status)
        return ret

    def wait_run(self, command, timeout=None):
        d = self.device
        start_time = time.time()
        self.wait_buffer_capacity()
        d.command(command)
        while True:
            status, mpos = d.get_status()
            logging.debug("status: %s", status)
            logging.debug("X: %s Y: %s", mpos[0], mpos[1])

            self.check_status(status)

            if timeout and (time.time() - start_time) > timeout:
                raise Device.DeviceMalfunction("Timeout")
            if status != "Run":
                logging.debug(f"pos: {self.pos}")
                return self.pos

    def homing_cycle(self, speed, target, update_home, timeout = None):
        d = self.device

        d.command("$21=1")
        try:
            self.wait_run(f"G1F{speed}X{target[0]}Y{target[1]}", timeout = timeout)
            raise RuntimeError("device go to very far point, maybe mechanical issue")
        except Device.DeviceNeedResetError:
            for idx in update_home:
                self.home[idx] = self.device.mpos[idx]
            self.reset_retract()

    def home_axis(self, target, update_home, disable_y=False):
        d = self.device

        while True:
            try:
                if disable_y:
                    self.disable_y()
                else:
                    self.enable_both()

                break
            except Device.DeviceNeedResetError:
                self.reset_retract()

        self.homing_cycle(1000, target, update_home)

        if disable_y:
            logging.info("additional retract for y")
            self.enable_both()
            self.wait_run(f"G1F1000Y{d.mpos[1] + self.param.y_init_retract}")

        self.homing_cycle(50, target, update_home, timeout = 10)

        if disable_y:
            logging.info("return y back")
            self.wait_run(f"G1F1000Y{d.mpos[1] - self.param.y_init_retract}")

    def home_a(self):
        self.home_axis((-2000, 0), [0, 1], disable_y = True)

    def home_b(self):
        self.home_axis((self.home[0] + self.param.w, self.home[1] - self.param.w), [1])

    def homing(self):
        try:
            self.home_a()
            self.home_b()
        except Device.DeviceNeedResetError:
            raise Device.DeviceMalfunction("Unhandled reset")

        self.wait_run(f"G1F{self.param.draw_speed}")

        logging.info(f"home: {self.home}")
    
    def make_move_command(self, x = None,y = None, speed = None) -> str:
        if speed is None:
            speed = self.param.draw_speed

        # cmd = f"G1F{speed}"
        cmd = ""
        if x is not None:
            cmd += f"X{self.home[0] + x}"
        if y is not None:
            cmd += f"Y{self.home[1] + y}"

        logging.debug(f"cmd: {cmd}")
        return cmd

    def move(self, x = None, y = None, speed = None):
        logging.debug(f"home: {self.home}")
        logging.info(f"move to: {x} {y}")

        return self.wait_run(self.make_move_command(x,y, speed))

    def move_async(self, x = None, y = None, speed = None):
        logging.info(f"move async to: {x} {y}")
        return self.run(self.make_move_command(x, y, speed))

    def reset_home(self, offset = (0, 0)):
        self.home = (self.device.mpos[0] + offset[0], self.device.mpos[1] + offset[1])

    @property
    def pos(self):
        mpos = self.device.mpos
        return (mpos[0] - self.home[0], mpos[1] - self.home[1])


    '''def run_cycle(self):
        while True:
            try:
                try:
                    self.wait_run("")
                except Device.DeviceNeedResetError:
                    self.reset_retract()

                self.home()

                self.ready = True

                while True:
                    target = self.get_task()
                    if target:
                        position = (self.device.home[0] + target[0], self.device.home[1] + target[0])
                        self.wait_run(f"G1F{self.param.draw_speed}X{zero_position[0]}Y{zero_position[1]}")

            except Device.DeviceMalfunction as e:
                self.ready = False
                logging.info(f"Device malfunction: {e}. Back to home")
                self.reset_retract()

    def interact(self, task):
        if not self.ready:
            return "not_ready"
        self.set_task(task)
        return "success"

    def set_task(self, task):
        self.task = task
        self.task_event.set()

    def get_task(self):
        self.task_event.wait()
        self.task_event.clear()
        return self.task
        # TODO if device not ready, return not_ready status
        # send command to run_cycle
    '''
