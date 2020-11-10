"""Утилиты для печати."""
import datetime as dt
import math
import numbers
from math import floor, isclose, isfinite, log10
from typing import Any, Optional

from dateutil.parser import parse
from diskcache import FanoutCache

# Кэш, в который можно сохранять на диск то, что уже было посчитано.
import settings

# from rich.traceback import install
# install()

cache = FanoutCache(settings.DATA_DIR / 'tmp/routes_cache/', shards=8, timeout=100)


def round_to_n(x: float, n=3) -> float:
    """Округляем до заданного количества знаков.

    Если int, то приводим
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


def parse_time(
    time_obj: Any, errors: str = 'raise', none: Any = None
) -> Optional[int]:
    """Парсим время и возвращаем количество секунд в unixtime Эта штуковина вроде как должна справляться почти
    с любыми форматами времени.

    :param time_obj:  время в каком-то виде
    :param errors:  что-то, что представляет из себя время
    :param none:  что вернуть вместо ошибки?
    :return: timestamp
    """
    try:
        if time_obj is None:
            return none
        elif isinstance(time_obj, (int, float)):
            return int(time_obj)
        elif isinstance(time_obj, str):
            try:
                return int(parse(time_obj).timestamp())
            except Exception:
                raise ValueError("Неизвестный формат времени")
        else:
            raise TypeError('Неизвестный тип времени')
    except (TypeError, ValueError) as e:
        if errors == 'raise':
            raise e
        else:
            return none


# Методы для стандартных форматов разных используемых айтемов

def format_float(f: float) -> str:
    return f'{f:.2f}'


def format_speed(
    speed: float,
    with_name: bool = False,
    with_units: bool = True,
    units: str = 'км/ч'
):
    if units == 'км/ч':
        speed *= 3.6
    elif units == 'м/c':
        pass  # noqa
    else:
        raise ValueError(f'Неизвестные единицы измерения {units}')

    res = ''
    res += with_name * 'Скорость: '
    res += format_float(speed)
    res += units * with_units

    return res


def format_distance(
    dist: float,
    with_name: bool = False,
    with_units: bool = True,
    units: str = 'км'
):
    if units == 'км':
        dist /= 1000
    elif units == 'м':
        pass  # noqa
    else:
        raise ValueError(f'Неизвестные единицы измерения {units}')

    res = ''
    res += with_name * 'Dist: '
    res += f'{dist:.1f}'
    res += units * with_units

    return res


def format_time(
    ts: int,
    with_date: bool = False,
    with_seconds: bool = False,
    with_name: bool = False,
):
    fmt = ""
    fmt += 'Время: ' * with_name
    fmt += "%m/%d/%Y " * with_date
    fmt += "%H:%M"
    fmt += ":%S" * with_seconds

    return dt.datetime.fromtimestamp(ts).strftime(fmt)


def format_time_window(
    start: int,
    end: int,
    with_name=False,
):
    """Формат в котором мы печатаем time_window."""
    res = ''
    res += 'TW: ' * with_name
    res += f"{format_time(start)}-{format_time(end)}"

    return res


def format_collection(
    collection: Any,
    sep: str = ', '
):
    """Формат в котором мы печатаем наборы."""
    data = sep.join(sorted(collection))
    if isinstance(collection, set):
        return f'{{{data}}}'
    elif isinstance(collection, list):
        return str(collection)
