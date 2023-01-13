import logging
import serial
import time
import termios
import tty
from getch import getch
from device import Device
from controller import ControllerParameters, Controller

logging.basicConfig(level=logging.INFO)

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
    d = Device("/dev/ttyUSB0", 115200)
    d.reset()
    logging.info("Device reset successfully")

    controller = Controller(d)

    while True:
        try:
            run_cycle(controller)
        except Device.DeviceMalfunction as e:
            logging.info(f"Device malfunction: {e}. Back to home")
            controller.reset_retract()

if __name__ == "__main__":
    main()

# grbl.stream("$120=50.000")
# grbl.stream("$121=50.000")
# grbl.stream("$110=2000.000")
# grbl.stream("$111=2000.000")
