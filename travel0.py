import serial
import time

class Device:
    class TimeoutError(Exception):
        def __init__(self, message):
            self.message = message

    def __init__(self, port_name, baudrate, retries = 3):
        self.ser = serial.Serial(port_name, baudrate=baudrate, timeout=1) # opens serial port
        self.retries = retries

    def get_status(self):
        response = self.command("?", wait_ok = False)
        parts = response.split("|")
        self.status = parts[0][1:]
        return self.status

    def reset(self):
        self.send_ctrl_x()
        retry_count = 0
        while retry_count < self.retries:
            try:
                response = self.read_response()
                if response.startswith("Grbl"):
                    return
            except Device.TimeoutError:
                print("Timeout while reading response from device, retrying...")
            retry_count += 1
        raise ValueError("Device is not responding after multiple resets.")

    def command(self, command, wait_ok = True):
        command = command + ("\r" if wait_ok else "")
        retry_count = 0
        while retry_count < self.retries:
            try:
                self.write_command(command)
                response = self.read_response()
                if "MSG:Reset to continue" in response:
                    raise ValueError("Device returned error: {}".format(response))
                if not wait_ok:
                    return response
                if response.startswith("ok"):
                    return
                retry_count += 1
            except Device.TimeoutError:
                retry_count += 1
                print("Timeout while reading response from device, retrying...")
        raise ValueError("Device is not responding after multiple retries.")
            
    def write_command(self, command):
        print(">", command)
        self.ser.write(command.encode())
        time.sleep(0.1)
    
    def read_response(self):
        response = self.ser.readline().decode().strip()
        print("<", response)
        if not response:
            raise Device.TimeoutError("Timeout while reading response from device.")
        return response
    
    def send_ctrl_x(self):
        print(">^X")
        self.ser.write(b'\x18')

# Usage example:
d = Device("/dev/ttyUSB0", 115200)

d.reset()
print("device resetted succesfully")

status = d.get_status()

if status == "Alarm":
    d.command("$X")

d.command("M08")
d.command("M05")
d.command("G1F500X-2000")

try:
    while True:
        print("status:", d.get_status())
        time.sleep(0.5)
except ValueError:
    d.reset()

status = d.get_status()

if status == "Alarm":
    d.command("$X")

# d.command("M03")