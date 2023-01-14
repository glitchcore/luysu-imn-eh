import time
import logging
import threading

from device import Device

class ControllerParameters:
    def __init__(self):
        self.w = 450
        self.retract_length = 2
        self.y_init_retract = 5
        self.draw_speed = 300

class Controller:
    def __init__(self, device, param = ControllerParameters()):
        self.device = device
        self.param = param
        self.ready = False
        self.task = None
        self.task_event = threading.Event()

    def reset_retract(self, ):
        d = self.device

        d.reset()
        d.command("$21=0")

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

    def wait_run(self, command, timeout=None):
        d = self.device
        start_time = time.time()
        d.command(command)
        while True:
            status, mpos = d.get_status()
            logging.debug("status: %s", status)
            logging.debug("X: %s Y: %s", mpos[0], mpos[1])
            if status != "Run":
                break
            if status == "Alarm":
                raise Device.DeviceNeedResetError("Alarm status")
            if timeout and (time.time() - start_time) > timeout:
                raise Device.DeviceMalfunction("Timeout")

    def homing_cycle(self, speed, target, update_home, timeout = None):
        d = self.device

        d.command("$21=1")
        try:
            self.wait_run(f"G1F{speed}X{target[0]}Y{target[1]}", timeout = timeout)
            raise RuntimeError("device go to very far point, maybe mechanical issue")
        except Device.DeviceNeedResetError:
            for idx in update_home:
                d.home[idx] = d.mpos[idx]
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

        self.homing_cycle(50, target, update_home, timeout = 5)

        if disable_y:
            logging.info("return y back")
            self.wait_run(f"G1F1000Y{d.mpos[1] - self.param.y_init_retract}")

    def home(self):
        d = self.device

        try:
            self.home_axis((-2000, 0), [0, 1], disable_y = True) # home A
            self.home_axis((d.home[0] + self.param.w, d.home[1] - self.param.w), [1]) # home B
        except Device.DeviceNeedResetError:
            raise Device.DeviceMalfunction("Unhandled reset")

    def run_cycle(self):
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
