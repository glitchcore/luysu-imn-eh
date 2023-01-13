import logging
import serial
import time

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
                logging.info("Timeout while resetting device, retrying...")
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
                    logging.info("Timeout while reading response from device, retrying...")
        raise ValueError("Device is not responding after multiple retries.")
            
    def write_command(self, command):
        logging.info("> %s", command)
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
            logging.debug("< %s", line.strip())
            response.append(line.strip())
        return response

    def send_ctrl_x(self):
        logging.info(">^X")
        self.ser.write(b'\x18')