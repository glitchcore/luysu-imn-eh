import numpy as np
from math import *

def get_transformation_matrix_dlt(normalized_rect, plane_rect):
    X = np.array([point[0] for point in normalized_rect])
    Y = np.array([point[1] for point in normalized_rect])
    u = np.array([point[0] for point in plane_rect])
    v = np.array([point[1] for point in plane_rect])
    A = np.zeros((8,9))
    A[::2] = np.column_stack([X, Y, np.ones_like(X), np.zeros_like(X), np.zeros_like(X), np.zeros_like(X), -u*X, -u*Y, -u])
    A[1::2] = np.column_stack([np.zeros_like(X), np.zeros_like(X), np.zeros_like(X), X, Y, np.ones_like(X), -v*X, -v*Y, -v])
    _, _, V = np.linalg.svd(A)
    H = V[-1].reshape(3,3)
    return H

def denormalize_coordinates(normalized_coord, trans_matrix):
    point = np.array([normalized_coord[0], normalized_coord[1], 1])
    denormalized_coord = np.matmul(trans_matrix, point)
    denormalized_coord = denormalized_coord[:2] / denormalized_coord[2]
    return denormalized_coord

normalized_rect = [(0, 0), (1, 0), (1, 1), (0, 1)]
# plane_rect = [(3, 8), (10, 5), (14, 20), (2, 24)]

trans_matrix = get_transformation_matrix_dlt(normalized_rect, plane_rect)

def normalize_test():
    for a in normalized_rect:
        print(denormalize_coordinates(a, trans_matrix))
    print(denormalize_coordinates((0.5, 0.5), trans_matrix))

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

def mach2grbl(mach, calib):
    return(
        (mach[0] - calib["init_a"]) * calib["R"],
        (mach[1] - calib["init_b"]) * calib["R"],
    )

class TraingleKinematic:
    def __init__(self, controller, calib, reference_points):
        self.controller = controller
        self.calib = calib
        self.pos = (0, 0)

        self.transform = get_transformation_matrix_dlt(normalized_rect, reference_points)

        self.update_from_controller()


    def reset_home(self):
        self.pos = [0, 0]
        self.controller.reset_home()

    def move(self, pos):
        self.pos = pos
        mach_pos = cart2mach(pos, self.calib)
        grbl_pos = mach2grbl(mach_pos, self.calib)
        self.controller.move(grbl_pos)

    def move_normalized(self, pos):
        self.move(denormalize_coordinates(pos, self.transform))

    def update_from_controller(self):
        self.pos = mach2cart(self.controller.pos, self.calib)

if __name__ == "__main__":
    normalize_test()