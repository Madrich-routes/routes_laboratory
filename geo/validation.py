import numpy as np


def check_distance_matrix(matrix: np.array, points: np.array):
    assert (matrix < 0).sum() == 0, 'В матрице есть отрицательные значения'
    assert np.issubdtype(matrix.dtype, np.int32), 'Матрица не приведена к интам'

    # lower_bound =
