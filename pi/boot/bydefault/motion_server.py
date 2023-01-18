import logging
import serial
import time
import termios
import tty
from getch import getch

from device import Device
from motion_controller import MotionControllerParameters, MotionController

from calib_gallery import CALIB
from geometry import TriangleKinematic

logging.basicConfig(level=logging.INFO)

'''
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

                controller.move(controller.pos[0] + move[0], controller.pos[1] + move[1])
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
'''
def arrow_move(controller):
    ARROW_STEP = 0.2

    while True:
        esc = ord(getch())
        if esc == 27:
            if ord(getch()) == 91:
                key = ord(getch())
                move = [0, 0]

                if key == 65:  # Up arrow key
                    move[0] -= ARROW_STEP
                    move[1] -= ARROW_STEP
                elif key == 66:  # Down arrow key
                    move[0] += ARROW_STEP
                    move[1] += ARROW_STEP
                elif key == 67:  # Right arrow key
                    move[0] += ARROW_STEP
                    move[1] -= ARROW_STEP
                elif key == 68:  # Left arrow key
                    move[0] -= ARROW_STEP
                    move[1] += ARROW_STEP

                controller.move(controller.pos[0] + move[0], controller.pos[1] + move[1])
                logging.info(f"pos: {controller.pos}")

        elif esc == ord('1'):
            ARROW_STEP = 0.1
            logging.info(f"step: {ARROW_STEP}")
        elif esc == ord('2'):
            ARROW_STEP = 0.5
            logging.info(f"step: {ARROW_STEP}")
        elif esc == ord('3'):
            ARROW_STEP = 1
            logging.info(f"step: {ARROW_STEP}")
        elif esc == ord('4'):
            ARROW_STEP = 5
            logging.info(f"step: {ARROW_STEP}")
        elif esc == ord('5'):
            ARROW_STEP = 10
            logging.info(f"step: {ARROW_STEP}")
        elif esc == ord('6'):
            ARROW_STEP = 20
            logging.info(f"step: {ARROW_STEP}")

        elif esc == ord('q'):
            break

def run_cycle(controller):
    try:
        controller.wait_run("")
    except Device.DeviceNeedResetError:
        controller.reset_retract()

    '''while True:
        controller.homing()
        zero_position = (controller.home[0] + 105, controller.home[1] + 348)
        controller.wait_run(f"G1F1000X{zero_position[0]}Y{zero_position[1]}")
    '''

    # controller.home_a() # home A
    
    controller.homing()
    controller.move(84.5, 415.5, 1000)

    print("set home position:")
    arrow_move(controller)

    triangle_controller = TriangleKinematic(controller, CALIB, CALIB["fragments"]["chr"])

    triangle_controller.reset_home()

    print("move, please:")
    arrow_move(triangle_controller)

    # arrow_move(controller)

    # controller.home_b()

    

def main():
    d = Device("/dev/serial/by-id/usb-1a86_USB2.0-Ser_-if00-port0", 115200)
    d.reset()
    logging.info("Device reset successfully")

    controller = MotionController(d)

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