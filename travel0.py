import serial
import time

import termios
import tty
from getch import getch

class Device:
    class TimeoutError(Exception):
        def __init__(self, message):
            self.message = message

    class DeviceNeedResetError(Exception):
        pass

    def __init__(self, port_name, baudrate, retries = 3):
        self.ser = serial.Serial(port_name, baudrate=baudrate, timeout=0.1) # opens serial port
        self.retries = retries
        self.status = ""
        self.mpos = (0,0)
        self.home = (0,0)

    def get_status(self):
        response = self.command("?", wait = "<", endline = False)
        parts = response.split("|")
        self.status = parts[0][1:]

        mpos_str = parts[1].split(":")[1]
        mpos_list = mpos_str.split(",")
        x = float(mpos_list[0])
        y = float(mpos_list[1])
        self.mpos = (x,y)
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

def limiter_cycle(device, command):
    try:
        d.command(command)
        while True:
            status, mpos = device.get_status()
            print("status:", status)
            print(f"X:{mpos[0]} Y:{mpos[1]}")
            if status != "Run":
                break
            time.sleep(0.5)
    except Device.DeviceNeedResetError:
        device.reset()

    status, mpos = device.get_status()
    print("status:", status)
    print(f"X:{mpos[0]} Y:{mpos[1]}")

    if status == "Alarm":
        device.command("$X")

def home_a(d):
    def homing_cycle(speed):
        limiter_cycle(d, f"G1F{speed}X-2000")
        d.home = (d.mpos[0], d.home[1])
        retract = d.home[0] + 2
        while True:
            limiter_cycle(d, f"G1F{speed}X{retract}")

            if(abs(d.mpos[0] - retract) < 0.01):
                break
    # B homing
    d.command("M08")
    d.command("M05")

    # fast homing
    homing_cycle(500)
    homing_cycle(50)

W = 420
def home_b(d):
    target = (d.home[0] + W, d.home[1] - W)

    def homing_cycle(speed):
        limiter_cycle(d, f"G1F{speed}X{target[0]}Y{target[1]}")
        d.home = (d.home[0], d.mpos[1])
        retract = d.home[1] + 2
        while True:
            limiter_cycle(d, f"G1F{speed}Y{retract}")

            if(abs(d.mpos[1] - retract) < 0.01):
                break
    # A homing
    d.command("M09")
    d.command("M05")

    # fast homing
    homing_cycle(500)
    homing_cycle(50)

def arrow_move():
    while True:
        esc = ord(getch())
        if esc == 27:
            if ord(getch()) == 91:
                key = ord(getch())
                move = [0, 0]

                if key == 65:  # Up arrow key
                    move[1] += 1
                elif key == 66:  # Down arrow key
                    move[1] -= 1
                elif key == 67:  # Right arrow key
                    move[0] += 1
                elif key == 68:  # Left arrow key
                    move[0] -= 1

                command = f"G1F200X{d.mpos[0] + move[0]}Y{d.mpos[1] + move[1]}"
                limiter_cycle(d, command)

        elif esc == 99:
            break

def main():
    # Usage example:
    d = Device("/dev/ttyUSB0", 115200)

    d.reset()
    print("device resetted succesfully")

    limiter_cycle(d, "")

    home_a(d)
    home_b(d)

    arrow_move()

if __name__ == "__main__":
    main()