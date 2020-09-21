from functools import lru_cache
from typing import Tuple

import numba as nb
import numpy as np

from data_structures.tour.base import Tour
from utils.algorithms import make_pair

Edge = Tuple[int, int]


class ArrayTour(Tour):

    def __hash__(self):
        return generate_hash(self.nodes)

    def distance(self):
        return get_length(self.nodes, self.problem.matrix)

    def prev(self, a: int):
        pass

    def next(self, a: int):
        pass

    def between(self, a: int, b: int, c: int):
        return between(len(self.nodes), a, b, c)

    def flip(self, a: int, b: int, c: int, d: int) -> None:
        pass

    def edges(self):
        return get_set(self.nodes)


@lru_cache
def generate_degrees(number: int, module: int, size: int) -> np.ndarray:
    """ Вычисление степеней 0 - size числа number по модулю module
    number: чьи степени ищем
    module: по какому модулю
    size: сколько степеней
    return: [1, number, number^2 % module ... number^(size -1)]
    """
    nums = np.zeros(size, dtype=np.int64)
    nums[0], nums[1] = 1, number
    for i in range(1, size):
        number = (number * number) % module
        nums[i] = number
    return nums


def generate_hash_from(tour: np.ndarray, number: int, module: int) -> int:
    """ Вычисление хеша для тура по туру и списку степенй
    tour: список городов
    number: чьи степени ищем
    return: хеш
    """
    degrees = generate_degrees(number, module, len(tour))
    return (tour * degrees % module).sum() % module


@nb.njit
def generate_hash(tour: np.ndarray, number=333667, module=909090909090909091) -> int:
    """ Вычисления  хеша по туру
    tour: список вершин
    number: чьи степени будем искать
    module: по какому модулю
    return: хеш
    """
    with nb.objmode(h='int64'):
        h = generate_hash_from(rotate_zero(tour), number, module)
    return h


@nb.njit(cache=True)
def rotate(tour: np.ndarray, num: int) -> np.ndarray:
    """ Сдвиг массива влево на n элементов
    tour: список вершин
    num: на сколько двигаем
    return: сдвинутый
    """
    if num == 0:
        return tour
    size, idx = len(tour), 0
    temp = np.zeros(size, dtype=nb.int64)
    for i in range(num, size):
        temp[idx] = tour[i]
        idx += 1
    for j in range(0, num):
        temp[idx] = tour[j]
        idx += 1
    return temp


@nb.njit(cache=True)
def rotate_zero(tour: np.ndarray) -> np.ndarray:
    """ Проворачиваем список так, что бы первым был ноль
    tour: список вершин
    return: свдинутый список
    """
    if tour[0] == 0:
        return tour
    return rotate(tour, np.where(tour == 0)[0][0])


@nb.njit(cache=True)
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


def get_inf(matrix: np.ndarray):
    """
    Длина ребра, такая, чтобы точно не попасть в тур
    """
    return get_length(np.arange(start=0, end=len(matrix)), matrix)


def get_set(tour: np.ndarray) -> Set[Tuple[int, int]]:
    """ Генерация набора ребер тура
    tour: список вершин
    return: set из ребер
    """
    edges = set()
    for i in range(len(tour)):
        edges.add(make_pair(tour[i - 1], tour[i]))
    return edges


@nb.njit(cache=True)
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
