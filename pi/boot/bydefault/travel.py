import logging
import serial
import time
import termios
import tty
from getch import getch

from device import Device
from controller import ControllerParameters, Controller

logging.basicConfig(level=logging.INFO)

def arrow_move(controller):
    ARROW_STEP = 0.5

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
                    move[0] += ARROW_STEP
                    move[1] += ARROW_STEP
                elif key == 66:  # Down arrow key
                    move[0] -= ARROW_STEP
                    move[1] -= ARROW_STEP
                elif key == 67:  # Right arrow key
                    move[0] -= ARROW_STEP
                    move[1] += ARROW_STEP
                elif key == 68:  # Left arrow key
                    move[0] += ARROW_STEP
                    move[1] -= ARROW_STEP

                controller.wait_run(f"G1F1000X{controller.device.mpos[0] + move[0]}Y{controller.device.mpos[1] + move[1]}")
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

    '''while True:
        controller.home()
        zero_position = (controller.device.home[0] + 105, controller.device.home[1] + 348)
        controller.wait_run(f"G1F1000X{zero_position[0]}Y{zero_position[1]}")
    '''

    # controller.home_axis((-2000, 0), [0, 1], disable_y = True) # home A
    
    controller.home()
    # (-409.508, -70.844)
    zero_position = (controller.device.home[0] + 90.5, controller.device.home[1] + 413.5)
    controller.wait_run(f"G1F1000X{zero_position[0]}Y{zero_position[1]}")

    # arrow_move(controller)

    #controller.home_axis(
    #    (controller.device.home[0] + controller.param.w, controller.device.home[1] - controller.param.w), [1])

    arrow_move(controller)

def main():
    d = Device("/dev/serial/by-id/usb-1a86_USB2.0-Ser_-if00-port0", 115200)
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
