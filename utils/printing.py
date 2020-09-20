"""
Утилиты для печати
"""
import math
import numbers
from math import isclose, isfinite, floor, log10
from typing import Any


def round_to_n(x: float, n=3) -> float:
    """
    Округляем до заданного количества знаков. Если int, то приводим
    """

    if isclose(x, 0):
        return 0

    if not isfinite(x):
        return x

    res = round(x, -int(floor(log10(abs(x)))) + (n - 1))

    if isclose(res, int(res)):
        res = int(res)

    return res


def is_number(a: Any) -> bool:
    return isinstance(a, numbers.Number) and math.isfinite(a)
