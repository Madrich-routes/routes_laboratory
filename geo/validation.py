import numpy as np

from geo.transforms import line_distance_matrix


def check_distance_matrix(
        matrix: np.array,
        points: np.array
):
    """
    Проверяем, что с матрицей расстояний все в порядке
    """
    assert (matrix > 0).all(), 'В матрице есть отрицательные значения'
    assert np.issubdtype(matrix.dtype, np.int32), 'Матрица не приведена к интам'
    assert (line_distance_matrix(points, points) <= matrix).all(), 'Не соблюдается нижнаяя граница'
