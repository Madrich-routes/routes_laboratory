from datetime import datetime
from typing import List, Tuple

import numpy as np

array = np.ndarray


def ts_to_rfc(ts: int) -> str:
    """Конвертируем unix timestamp в RFC3339 . В pragmatic время представлено в таком формате.
    Добавлена поправка для Windows на 86400, т.к. минимальный Unix timestamp 86400
    >>> ts_to_rfc(0)
    '1970-01-01T03:00:00Z'
    Parameters
    ----------
    ts : Unix timestamp
    Returns
    -------
    Время в формате RFC3339  в UTC таймзоне c Z на конце.
    """
    return datetime.fromtimestamp(ts).isoformat() + "Z"


def convert_tw(time_windows: List[Tuple[int, int]]) -> List[Tuple[str, str]]:
    """Конвретируем временное окно из таймстампов в RFC3339.
    >>> convert_tw([(0, 0)])
    [('1970-01-01T03:00:00Z', '1970-01-01T03:00:00Z')]
    Parameters
    ----------
    time_windows : Лист временных окон в unix timestamp
    Returns
    -------
    Лист временных окон в iso
    """
    return [(ts_to_rfc(tw[0]), ts_to_rfc(tw[1])) for tw in time_windows]


def str_to_ts(t: str) -> int:
    return int(datetime.strptime(t, '%Y-%m-%dT%H:%M:%SZ').timestamp())


def to_list(points: array) -> List[Tuple[float, float]]:
    """array n * 2 to List[Point], Point = float, float
    :param points: points in ndarray format
    :return: points in list format
    """
    temp = []
    for point in points:
        temp.append((point[0], point[1]))
    return temp
