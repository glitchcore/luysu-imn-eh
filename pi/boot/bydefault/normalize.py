import numpy as np

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
plane_rect = [(0.1, 0.1), (10, 0.2), (10, 20), (0.1, 20)]
trans_matrix = get_transformation_matrix_dlt(normalized_rect, plane_rect)

def normalize_test():
    for a in normalized_rect:
        print(denormalize_coordinates(a, trans_matrix))
    print(denormalize_coordinates((0.5, 0.5), trans_matrix))

if __name__ == "__main__":
    normalize_test()