import numba as nb
import numpy as np

array = np.ndarray


@nb.njit
def generate_points(n: int, min_x=55.65, max_x=55.82, min_y=37.45, max_y=37.75) -> array:
    """Массив рандомных точек в квадрате."""
    diff_x, diff_y = max_x - min_x, max_y - min_y
    return np.random.random_sample((n, 2)) * np.array([diff_x, diff_y]) + np.array([min_x, min_y])


@nb.njit
def generate_windows(n: int, segment: int, parts=4) -> array:
    """Окна, тупо может в сегмент или нет.

    :param n: кол-во точек в наборе
    :param segment: размер сегмента в минутах
    :param parts: сколько сегментов
    :return: массив расписаний на каждый сегмент, если [0, 0] то пропуск
    """
    # TODO: починить
    windows = np.zeros((n, parts, 2), dtype=nb.int64)
    tmp = np.random.randint(0, 2, size=(n, parts))

    for i, point in enumerate(windows):
        for j, window in enumerate(point):
            if not tmp[i][j]:
                continue
            window[0], window[1] = segment * j, segment * (j + 1)

    return windows


@nb.njit
def generate_time(n: int, mul=500) -> array:
    return np.array([int(t) for t in np.random.random_sample(n) * mul])


@nb.njit
def generate_customer_weights(n: int, mul=10) -> array:
    return np.array([(int(t) + 1) * mul for t in np.random.random_sample(n) * mul])


@nb.njit
def generate_car_weights(n: int, mul=50) -> array:
    return np.array([(int(t) + 1) * mul for t in np.random.random_sample(n) * mul])


@nb.njit
def generate_car_max_distance(n: int, mul=1000) -> array:
    return np.array([(int(t) + 1) * mul for t in np.random.random_sample(n) * mul])


@nb.njit
def generate_car_max_deliveries(n: int, mul=10) -> array:
    return np.array([(int(t) + 1) * mul for t in np.random.random_sample(n) * mul])


@nb.njit
def generate_car_max_trips(n: int, mul=5) -> array:
    return np.array([(int(t) + 1) * mul for t in np.random.random_sample(n) * mul])
