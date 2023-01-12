from math import *
from calib1 import *

def mach2cart(mach, calib):
    p, q = mach

    return (
        (p**2 - q**2 + calib["W"]**2)/(2 * calib["W"]),
        sqrt(p**2 - (p**2 - q**2 + calib["W"]**2)**2/(4 * calib["W"]**2))
    )

def cart2mach(cart, calib):
    x, y = cart

    return (
        sqrt(x**2 + y**2),
        sqrt((calib["W"] - x)**2 + y**2)
    )

def denorm_coords(c, calib, workspace):
    return(
        workspace[0] + c[0] * workspace_size[0],
        workspace[1] + c[1] * workspace_size[1],
    )

def mach2grbl(mach, calib):
    return(
        (mach[0] - calib["init_a"]) * calib["R"],
        (mach[1] - calib["init_b"]) * calib["R"],
    )
    '''return(
        (mach[0] - init[0])/ step[0],
        (mach[1] - init[1])/ step[1],
    )'''

'''
def grbl2mach(grbl):
    return(
        init[0] + grbl[0] * step[0],
        init[1] + grbl[1] * step[1],
    )
'''


'''
for machine_coord in machine_coords:
    print(mach2cart(grbl2mach(machine_coord)))
'''

targets = [
    (1, -1),
    (0, -1),
    (0, 0),
    (1, 0)
]

def make_grbl(t, calib):
    workspace = mach2cart((calib["init_a"], calib["init_b"]), calib)

    carts = [denorm_coords(target, calib, workspace) for target in t]
    machs = [cart2mach(cart, calib) for cart in carts]
    grbls = [mach2grbl(mach, calib) for mach in machs]

    '''print("carts")
    for cart in carts:
        print(cart)

    print("machs")
    for mach in machs:
        print(mach)
    '''
    return grbls

def get_error(a, target, debug=False):
    s = 0
    for p in zip(a, target):
        dx = (p[0][0] - p[1][0]) ** 2
        dy = (p[0][1] - p[1][1]) ** 2
        if debug:
            print("x:", p[0][0], p[1][0], "dx", dx)
            print("y:", p[0][1], p[1][1], "dy", dx)
        s += dx + dy

    return s

def compute_gradient(calib, param_name, eps=1e-8):
    calib[param_name] += eps
    error_plus = get_error(target_coords, make_grbl(targets, calib))
    calib[param_name] -= 2*eps
    error_minus = get_error(target_coords, make_grbl(targets, calib))
    calib[param_name] += eps
    # print("grad:", error_plus, error_minus)
    return (error_plus - error_minus) / (2*eps)

def optimize_calibration(calib, target_coords, delta=0.1, max_iter=1000, lr=1e-6):
    for i in range(max_iter):
        result = make_grbl(targets, calib)
        error = get_error(target_coords, result)
        if error < delta:
            break
            
        # Compute gradient of error function w.r.t. calibration parameters
        grad_W = compute_gradient(calib, 'W')
        # grad_init_a = compute_gradient(calib, 'init_a')
        # grad_init_b = compute_gradient(calib, 'init_b')
        # grad_R = compute_gradient(calib, 'R')

        # Update calibration parameters
        calib['W'] -= lr * grad_W
        # calib['init_a'] -= lr * grad_init_a
        # calib['init_b'] -= lr * grad_init_b
        # calib['R'] -= lr * grad_R

        # print(calib, error)
        
    return calib

print("before")
grbls = make_grbl(targets, INIT_CALIB)
e = get_error(target_coords, grbls, debug=False)
print("e", e)

# print("after")
# calib = optimize_calibration(INIT_CALIB, target_coords)
# calib = INIT_CALIB
# grbls = make_grbl(targets, calib)
# e = get_error(target_coords, grbls, debug=True)

print("grbl")
for grbl in grbls:
    print(grbl)
# print("e", e)