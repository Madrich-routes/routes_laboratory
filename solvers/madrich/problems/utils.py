from copy import deepcopy
from math import sqrt
from typing import Tuple

import numba as nb
import numpy as np

array = np.ndarray
vector = nb.typed.List


@nb.njit(parallel=True)
def adjacency_matrix(points: array) -> array:
    """Матрица смежности."""
    size = points.shape[0]
    matrix = np.zeros(shape=(size, size))
    for idx in range(0, size):
        for idy in range(idx + 1, size):
            distance = sqrt((points[idy][0] - points[idx][0]) ** 2 + (points[idy][1] - points[idx][1]) ** 2)
            matrix[idx][idy] = matrix[idy][idx] = distance
    return matrix


@nb.njit
def rotate(tour: array, num: int) -> array:
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


@nb.njit
def rotate_zero(tour: array) -> array:
    """ Проворачиваем список так, что бы первым был ноль
    tour: список вершин
    return: свдинутый список
    """
    if tour[0] == 0:
        return tour
    return rotate(tour, np.where(tour == 0)[0][0])


@nb.njit
def rotate_value(tour: array, value: int) -> array:
    """ Проворачиваем список так, что бы первым был value
    tour: список вершин
    return: свдинутый список
    """
    if tour[0] == value:
        return tour
    return rotate(tour, np.where(tour == value)[0][0])


@nb.njit
def mix(tour: array, iterations: int) -> None:
    """Попытка сломать тур.

    Ломается текущий сохраненный. Идея в том, что если не получилось выйти из текущего локального оптимума, с
    перемешанными n вершинами, то стоит попробовать перемешать еще n.
    """
    for _ in range(iterations):
        size = len(tour) - 1
        x = np.random.randint(0, size)
        while x == (y := np.random.randint(0, size)):
            continue
        tour[x], tour[y] = tour[y], tour[x]


def swap(route: list, x: int, y: int) -> list:
    """Переворот куска тура: [x, y], включительно!

    :param route:
    :param x: индекс
    :param y: индекс
    :return: измененный список
    """
    route = deepcopy(route)
    size, temp = len(route), 0
    if x < y:
        temp = (y - x + 1) // 2
    elif x > y:
        temp = ((size - x) + y + 2) // 2
    for i in range(temp):
        first, second = (x + i) % size, (y - i) % size
        route[first], route[second] = route[second], route[first]
    return route


def three_opt_exchange(route: list, best_exchange: int, nodes: tuple) -> list:
    """ Изменение тура, после нахождения лучшего изменения 3-opt
    route:
    best_exchange: Тип замены
    nodes: Города
    return: Новый список городов
    """
    route = deepcopy(route)
    x, y, z = nodes
    s = len(route)
    b, c, d, e = (x + 1) % s, y % s, (y + 1) % s, z % s
    if best_exchange == 0:
        route = swap(swap(route, b, e), b, b + (e - d))
    elif best_exchange == 1:
        route = swap(swap(swap(route, b, e), b, b + (e - d)), e - (c - b), e)
    elif best_exchange == 2:
        route = swap(swap(route, b, e), e - (c - b), e)
    elif best_exchange == 3:
        route = swap(swap(route, d, e), b, c)
    elif best_exchange == 4:
        route = swap(route, b, e)
    elif best_exchange == 5:
        route = swap(route, d, e)
    elif best_exchange == 6:
        route = swap(route, b, c)
    return route


def cross(route1: list, route2: list, it1: int, it2: int, it3: int, it4: int) -> Tuple[list, list]:
    """ Cross-оператор - обмен кусками туров
    :param route1: тур один
    :param route2: тур два
    :param it1: тур один - начало куска
    :param it2: тур один - конец куска
    :param it3: тур два - начала куска
    :param it4: тур два - конец куска
    :return: новые туры
    """
    size1, size2 = len(route1), len(route2)
    new_size1 = size1 - (it2 - it1) + (it4 - it3)
    new_size2 = size2 - (it4 - it3) + (it2 - it1)
    new_route1 = [route1[0]] * new_size1  # shit
    new_route2 = [route2[0]] * new_size2  # shit

    for i in range(it1):
        new_route1[i] = route1[i]
    for i in range(it4 - it3 + 1):
        new_route1[i + it1] = route2[i + it3]
    for i in range(1, size1 - it2):
        new_route1[i + it1 + (it4 - it3)] = route1[i + it2]

    for i in range(it3):
        new_route2[i] = route2[i]
    for i in range(it2 - it1 + 1):
        new_route2[i + it3] = route1[i + it1]
    for i in range(1, size2 - it4):
        new_route2[i + it3 + (it2 - it1)] = route2[i + it4]

    return new_route1, new_route2


def replace(route1: list, route2: list, it1: int, it2: int) -> Tuple[list, list]:
    """Перемещение точки из тура 2 в тур 1.

    :param route1: тур 1
    :param route2: тур 2
    :param it1: куда вставить
    :param it2: откуда вытащить
    :return: новые туры
    """
    size1, size2 = len(route1), len(route2)
    new_route1 = [route1[0]] * (size1 + 1)  # shit
    new_route2 = [route2[0]] * (size2 - 1)  # shit

    for i in range(size1 + 1):
        if i == it1:
            new_route1[i] = route2[it2]
        elif i < it1:
            new_route1[i] = route1[i]
        else:
            new_route1[i] = route1[i - 1]

    for i in range(size2 - 1):
        if i < it2:
            new_route2[i] = route2[i]
        else:
            new_route2[i] = route2[i + 1]

    return new_route1, new_route2
