from typing import Union, List, Tuple

import numpy as np

from madrich.problems.utils import adjacency_matrix
from madrich.utils import to_array

array = np.ndarray
Point = Tuple[float, float]
Matrices = Union[array, List[array]]

coefficient = {
    'distance': 9.67,
    'travelTime': 1.3
}


def generate_matrix(points: Union[array, List[Point]], factor='travelTime') -> array:
    matrix = adjacency_matrix(points) * 1e4
    return (np.random.random_sample(matrix.shape) * matrix / 2 + matrix) * coefficient[factor]


def get_matrix(points: Union[array, List[Point]], factor: Union[str, List[str]] = 'travelTime') -> Matrices:
    """ Возвращает ассиметричные матрицы смежности
    :param factor:
    :param points: точки
    :return: матрица, одна, фиговая
    """
    points = points if type(points) == np.ndarray else to_array(points)
    if type(factor) is list:
        output = []
        for f in factor:
            output.append(generate_matrix(points, f))
    else:
        output = generate_matrix(points, factor)
    return output


def get_matrices(points: Union[array, List[Point]], max_cost: int, split=15,
                 factor: Union[str, List[str]] = 'travelTime') -> Matrices:
    """ Возвращает нужное кол-во матриц смежностей
    :param factor:
    :param points: точки
    :param max_cost: сколько времени со старта пройдет
    :param split: минуты
    :return: много матриц
    """
    split *= 60
    size = len(points)
    length = int(np.ceil(max_cost / split))

    if type(factor) is str:
        matrices = np.zeros(shape=(length, size, size), dtype=np.int64)
        for i in range(length):
            matrices[i] = get_matrix(points, factor)
    else:
        matrices = []
        for f in factor:
            tmp = np.zeros(shape=(length, size, size), dtype=np.int64)
            for i in range(length):
                tmp[i] = get_matrix(points, f)
            matrices.append(tmp)

    return matrices
