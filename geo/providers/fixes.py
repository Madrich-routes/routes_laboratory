"""
Тут расположены разлиные исправления данных, которые мы получаем на от провайдера
"""
from typing import Tuple


def fix_drivers(
        t: int,
        d: int
) -> Tuple[int, int]:
    """
    Исправляем неправдоподобную скорость водителя

    Parameters
    ----------
    t : время в секундах
    d : расстояние

    Returns
    -------

    """
    if t != 0 and 5 < d / t < 13:
        if t > 3600:
            return d / 12, d
        elif d > 1e5:
            return t, t * 12
        else:
            return d / 12, d
    return t, d


def fix_bicycle(
        t: int,
        d: int
) -> Tuple[int, int]:
    """
    Исправляем неправдоподобную скорость перемещения водителяы

    Parameters
    ----------
    t : время в секундах
    d : расстояние

    Returns исправленное время и расстояние
    -------

    """
    if t != 0 and 2 < d / t < 5:
        if t > 2 * 60 * 60:
            return d / 4, d
        elif d > 100 * 1000:
            return t, t * 4
        else:
            return d / 4, d
    return t, d
