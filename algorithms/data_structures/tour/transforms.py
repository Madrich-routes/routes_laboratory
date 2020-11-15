import numba as nb
import numpy as np

from utils.types import Array


@nb.njit()
def index(
    tour: Array,
    item: int,
) -> int:
    """
    Найти первый индекс значения

    >>> index(np.array([1, 0, 2, 4]), item=2)
    2

    Parameters
    ----------
    tour :  Массив
    item : Значение

    Returns
    -------
    Первый индекс значения
    """
    for idx, val in np.ndenumerate(tour):
        if val == item:
            return idx[0]

    return -1
    # Ексепшены и прочее нельзя в нумбе, поэтому -1


@nb.njit()
def rotate(tour: Array, num: int) -> Array:
    """ Сдвиг массива влево на n элементов

    >>> rotate(np.array([1, 0, 2, 4]), num=2)
    array([2, 4, 1, 0])

    Parameters
    ----------
    tour: список вершин
    num: на сколько двигаем

    Returns
    -------
    Cдвинутый
    """
    return np.roll(tour, num)


@nb.njit()
def rotate_zero(tour: Array) -> Array:
    """ Проворачиваем список так, что бы первым был ноль

    >>> rotate_zero(np.array([1, 0, 2, 4], dtype=np.int32))
    array([0, 2, 4, 1], dtype=int32)

    Parameters
    ----------
    tour: список вершин

    Returns
    -------
    Cдвинутый до 0
    """
    idx = index(tour, 0)
    if idx == -1:
        raise ValueError('Не нашли 0')

    return rotate(tour, -idx)


def get_set(tour: np.ndarray):
    """
     Генерация набора ребер тура
    tour: список вершин
    return: set из ребер
    """
    return {make_pair(tour[i - 1], tour[i]) for i in range(len(tour))}
