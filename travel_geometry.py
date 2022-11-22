from math import *
from calib0 import *

workspace_size = ((workspace[2] - workspace[0]), (workspace[3] - workspace[1]))

def denorm_coords(c):
    return(
        workspace[0] + c[0] * workspace_size[0],
        workspace[1] + c[1] * workspace_size[1],
    )

def mach2grbl(mach):
    return(
        (mach[0] - init[0])/ step[0],
        (mach[1] - init[1])/ step[1],
    )

def grbl2mach(grbl):
    return(
        init[0] + grbl[0] * step[0],
        init[1] + grbl[1] * step[1],
    )

def cart2mach(cart):
    x, y = cart

    return (
        sqrt(x**2 + y**2),
        sqrt((W - x)**2 + y**2)
    )

def mach2cart(mach):
    p, q = mach

    return (
        (p**2 - q**2 + W**2)/(2 * W),
        sqrt(p**2 - (p**2 - q**2 + W**2)**2/(4 * W**2))
    )

'''
for machine_coord in machine_coords:
    print(mach2cart(grbl2mach(machine_coord)))
'''

targets = [
    (1, 1),
    (0, 1),
    (0, 0),
    (1, 0)
]

for target in targets:
    print(mach2grbl(cart2mach(denorm_coords(target))))