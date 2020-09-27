from typing import Tuple

import numba as nb
import numpy as np
from numba.experimental import jitclass


@jitclass(spec=[('frequency', nb.int32), ('total', nb.int32), ('iter', nb.int32)])
class IterationCounter:
    """
    Быстрый и тупой счетчик итераций цикла, который печатает раз в какое-то время
    """

    def __init__(self, frequency: int, total: int):
        self.frequency = frequency
        self.total = total
        self.iter = 0

    def print_progress(self) -> None:
        self.iter += 1  # печатаем итерацию
        if self.iter % 10000 == 0:
            print(int(self.iter / self.total * 100), '%')


@nb.njit()
def make_pair(i: int, j: int) -> Tuple[int, int]:
    """
    Правильная пара для упрощения хранения ребер
    i, j: индексы ребер
    return: правильное ребро
    """
    return (i, j) if i > j else (j, i)


@nb.njit()
def rotate(tour: np.ndarray, num: int) -> np.ndarray:
    """
    Сдвиг массива влево на n элементов
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


@nb.njit()
def get_length(tour: np.ndarray, matrix: np.ndarray) -> float:
    """
    Взятие длины по матрице смежности и туру в виде последовательных вершин
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
    """
    Проверка находится ли third между first и second
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


@nb.njit()
def around(tour: np.ndarray, it: int) -> tuple:
    """
    Возвращает predecessor and successor вершины t
    tour: список городов
    it: индекс вырешины t
    return: ((index suc, suc), (index pred, pred))
    """
    s = len(tour)
    return ((it + 1) % s, tour[(it + 1) % s]), ((it - 1) % s, tour[(it - 1) % s])


@nb.njit()
def swap(tour: np.ndarray, x: int, y: int) -> np.ndarray:
    """
    Переворот куска тура: [x, y], включительно!
    tour: список городов
    x, y: индексы
    return: измененный список
    """
    size, temp = len(tour), 0
    if x < y:
        temp = (y - x + 1) // 2
    elif x > y:
        temp = ((size - x) + y + 2) // 2
    for i in range(temp):
        first, second = (x + i) % size, (y - i) % size
        tour[first], tour[second] = tour[second], tour[first]
    return tour


def start_tw(time_windows: np.ndarray, travel_times: np.ndarray):
    """
    Вычисляем временное окно, в которое нужно начать объезжать последовательность точек,
    чтобы попасть во все временные окна и не ждать.

    Эта функция умеет работать только с единственным временным окном.
    TODO: научить ее работать с множественными временными окнами
    Это функция не сможет нормально работать при поддержке пробок.

    time_windows — массив временных окон [(start, end)...] длиной
    travel_times[i] — время проезда от вершины i до i+1
    """

    assert len(time_windows) == len(travel_times) + 1, f'Неправильная длина {len(time_windows)}, {len(travel_times)}'

    if not isinstance(time_windows, np.ndarray):
        time_windows = np.array(time_windows)

    windows = time_windows - np.cumsum([0] + travel_times)
    start = windows[:, 0].max()
    end = windows[0, :].min()

    return start, end
