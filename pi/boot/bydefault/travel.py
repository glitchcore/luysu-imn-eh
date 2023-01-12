import serial
import time

import termios
import tty
from getch import getch

class Device:
    class TimeoutError(Exception):
        def __init__(self, message=""):
            self.message = message

    class DeviceNeedResetError(Exception):
        def __init__(self, message=""):
            self.message = message

    class DeviceMalfunction(Exception):
        def __init__(self, message=""):
            self.message = message

    def __init__(self, port_name, baudrate, retries = 3):
        self.ser = serial.Serial(port_name, baudrate=baudrate, timeout=0.1) # opens serial port
        self.retries = retries
        self.status = ""
        self.mpos = (0,0)
        self.home = [0,0]

    def get_status(self):
        retry_count = 0
        while retry_count < self.retries:
            response = self.command("?", wait = "<", endline = False)
            parts = response.split("|")
            status = parts[0][1:]

            if status in ["Alarm", "Run", "Idle"]:
                self.status = status
                mpos_str = parts[1].split(":")[1]
                mpos_list = mpos_str.split(",")
                x = float(mpos_list[0])
                y = float(mpos_list[1])
                self.mpos = (x,y)
                break

        return (self.status, self.mpos)

    def reset(self):
        while True:
            self.send_ctrl_x()
            try:
                response = self.read_response()
                for line in response:
                    if "Grbl" in line:
                        return
            except Device.TimeoutError:
                print("Timeout while resetting device, retrying...")
        raise ValueError("Device is not responding after reset.")

    def command(self, command, wait = "ok", endline = True):
        command = command + ("\r" if endline else "")

        retry_count = 0
        while retry_count < self.retries:
            try:
                self.write_command(command)
                response = self.read_response()
                for line in response:
                    if "MSG:Reset to continue" in line:
                        raise Device.DeviceNeedResetError
                    if line.startswith(wait):
                        return line
            except Device.TimeoutError as e:
                    retry_count += 1
                    print("Timeout while reading response from device, retrying...")
        raise ValueError("Device is not responding after multiple retries.")
            
    def write_command(self, command):
        print(">", command)
        self.ser.write(command.encode())
        time.sleep(0.1)

    def read_response(self):
        response = []
        while True:
            line = self.ser.readline().decode()
            if not line:
                if not response:
                    time.sleep(0.5)
                    line = self.ser.readline().decode()
                    if not line:
                        raise Device.TimeoutError("Read timeout")
                else:
                    break
            print("<", line.strip())
            response.append(line.strip())
        return response
    
    def send_ctrl_x(self):
        print(">^X")
        self.ser.write(b'\x18')

class ControllerParameters:
    def __init__(self):
        self.w = 450
        self.retract_length = 2
        self.y_init_retract = 5

class Controller:
    def __init__(self, device, param = ControllerParameters()):
        self.device = device
        self.param = param

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
                print("status:", status)
                print(f"X:{mpos[0]} Y:{mpos[1]}")
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
            print("status:", status)
            print(f"X:{mpos[0]} Y:{mpos[1]}")
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
            print("additional retract for y")
            self.enable_both()
            self.wait_run(f"G1F1000Y{d.mpos[1] + self.param.y_init_retract}")

        self.homing_cycle(50, target, update_home, timeout = 5)

        if disable_y:
            print("return y back")
            self.wait_run(f"G1F1000Y{d.mpos[1] - self.param.y_init_retract}")

    def home(self):
        d = self.device

        try:
            self.home_axis((-2000, 0), [0, 1], disable_y = True) # home A
            self.home_axis((d.home[0] + self.param.w, d.home[1] - self.param.w), [1]) # home B
        except Device.DeviceNeedResetError:
            raise Device.DeviceMalfunction("Unhandled reset")

def arrow_move(d):
    ARROW_STEP = 2

    prefix = input("Please input the prefix of the file name: ")
    N = 0
    points = []

    while True:
        esc = ord(getch())
        if esc == 27:
            if ord(getch()) == 91:
                key = ord(getch())
                move = [0, 0]

                if key == 65:  # Up arrow key
                    move[1] += ARROW_STEP
                elif key == 66:  # Down arrow key
                    move[1] -= ARROW_STEP
                elif key == 67:  # Right arrow key
                    move[0] += ARROW_STEP
                elif key == 68:  # Left arrow key
                    move[0] -= ARROW_STEP

                command = f"G1F200X{d.mpos[0] + move[0]}Y{d.mpos[1] + move[1]}"
                limiter_cycle(d, command)
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
            break

def run_cycle(controller):
    try:
        controller.wait_run("")
    except Device.DeviceNeedResetError:
        controller.reset_retract()

    while True:
        controller.home()
        zero_position = (controller.device.home[0] + 105, controller.device.home[1] + 348)
        controller.wait_run(f"G1F1000X{zero_position[0]}Y{zero_position[1]}")

    arrow_move(d)

def main():
    # Usage example:
    d = Device("/dev/ttyUSB0", 115200)
    d.reset()
    print("device resetted succesfully")

    controller = Controller(d)

    while True:
        try:
            run_cycle(controller)
        except Device.DeviceMalfunction as e:
            print("device malfunction", e, "back to home")
            controller.reset_retract()

if __name__ == "__main__":
    main()

# grbl.stream("$120=50.000")
# grbl.stream("$121=50.000")
# grbl.stream("$110=2000.000")
# grbl.stream("$111=2000.000")