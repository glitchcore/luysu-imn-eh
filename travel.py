from gerbil.gerbil import Gerbil
from time import sleep

# M03 off X, M05 on X
# M08 off Y, M09 on Y

# M08
# M05
# X-500

def my_callback(eventstring, *data):
    args = []
    for d in data:
        args.append(str(d))
    print("MY CALLBACK: event={} data={}".format(eventstring.ljust(30), ", ".join(args)))
    # Now, do something interesting with these callbacks

grbl = Gerbil(my_callback)
# grbl.setup_logging()

grbl.cnect("/dev/ttyUSB0", 115200)

grbl.poll_start()

sleep(2)

# grbl.stream("$120=50.000")
# grbl.stream("$121=50.000")
# grbl.stream("$110=2000.000")
# grbl.stream("$111=2000.000")

sleep(1)

grbl.stream("M08")
grbl.stream("M05")
grbl.stream("X-500")

'''
grbl.stream("G0X0Y0")
grbl.stream("X10Y0")
grbl.stream("X10Y10")
grbl.stream("X0Y10")
grbl.stream("X0Y0")

grbl.job_new()
grbl.load_file("1.gcode")
grbl.job_run()
'''

sleep(10)

grbl.disconnect()