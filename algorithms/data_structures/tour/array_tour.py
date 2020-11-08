from functools import lru_cache
from typing import Tuple

import numba as nb
import numpy as np

from algorithms.data_structures.tour.base import Tour
from algorithms.data_structures.tour.hashes import generate_hash
from algorithms.data_structures.tour.transforms import get_set
from utils.algorithms import make_pair

Edge = Tuple[int, int]


class ArrayTour(Tour):
    """Просто набор вершин."""

    def __hash__(self):
        return generate_hash(self.nodes)

    def distance(self):
        return get_length(self.nodes, self.problem.matrix)

    def prev(self, a: int):
        return (a - 1) % self.size

    def next(self, a: int):
        return (a + 1) % self.size

    def between(self, a: int, b: int, c: int):
        return between(len(self.nodes), a, b, c)

    def flip(self, a: int, b: int, c: int, d: int) -> None:
        # TODO:
        raise NotImplementedError

    def edges(self):
        return get_set(self.nodes)


@nb.njit()
def get_length(tour: np.ndarray, matrix: np.ndarray) -> float:
    """ Взятие длины по матрице смежности и туру в виде последовательных вершин
    tour: список вершин
    matrix: матрица весов
    return: длина
    """
    length = matrix[tour[0]][tour[-1]]
    for idx in range(len(tour) - 1):
        length += matrix[tour[idx]][tour[idx + 1]]
    return length


@nb.njit()
def between(size: int, first: int, second: int, third: int) -> bool:
    """ Проверка находится ли third между first и second
    size: размер тура
    first, second, third: индексы вершин
    return: между?
    """
    if first < second:  # [ ... start -> ... search ... <- end ... ]
        if first < third < second:
            return True
    else:  # [ ? ... <- end ... start -> ... ? ]
        if 0 <= third < second or first < third < size:
            return True
    return False
