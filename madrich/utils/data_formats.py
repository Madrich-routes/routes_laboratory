"""Утилиты для печати."""
import datetime as dt
import math
import numbers
from math import floor, isclose, isfinite, log10
from typing import Any, Optional

from dateutil.parser import parse
from diskcache import FanoutCache

# Кэш, в который можно сохранять на диск то, что уже было посчитано.
from madrich.config import settings

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
    """Определяем, является ли объект конечным числом.

    Parameters
    ----------
    a : Объект

    Returns
    -------
    {True, False}
    """
    return isinstance(a, numbers.Number) and math.isfinite(a)


def parse_time(
    time_obj: Any, errors: str = 'raise', none: Any = None
) -> Optional[int]:
    """Парсим время и возвращаем количество секунд в unixtime.

    Эта штуковина вроде как должна справляться почти
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
    """Форматируем float для вывода на экран.

    Parameters
    ----------
    f : Число, которое форматируем

    Returns
    -------
    Отформатированная строка
    """
    return f'{f:.2f}'


def format_speed(
    speed: float,
    with_name: bool = False,
    with_units: bool = True,
    units: str = 'км/ч'
) -> str:
    """ Стандартным образом форматируем скорость
    Parameters
    ----------
    speed : Сама скорость
    with_name : Печатать ли, что это скорость?
    with_units : Печатать ли, единицы измерения
    units : В каких единицах показывать?

    Returns
    -------
    Отформатированную строку
    """
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
) -> str:
    """Красиво форматируем расстояние.

    Parameters
    ----------
    dist : Расстояние
    with_name : Печатать, что это расстояние
    with_units : Печатать единицы
    units : Какие единицы использовать

    Returns
    -------
    Строка с представлением расстояния
    """
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
) -> str:
    """Красиво форматируем время.

    Parameters
    ----------
    ts : Таймстамп
    with_date : Печатать дату
    with_seconds : Печатать секунды
    with_name : Печатать, что это время

    Returns
    -------
    """
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
) -> str:
    """Формат в котором мы печатаем time_window.

    Parameters
    ----------
    start : Таймстамп начала
    end : Таймстамп конца
    with_name : Печатать что это TW

    Returns
    -------
    Строку с представлением коллекции
    """
    res = ''
    res += 'TW: ' * with_name
    res += f"{format_time(start)}-{format_time(end)}"

    return res


def format_collection(
    collection: Any,
    sep: str = ', '
) -> str:
    """Формат в котором мы печатаем набор значений.

    Parameters
    ----------
    collection : коллекция значений
    sep : разделитель

    Returns
    -------
    Строку с представление коллекции
    """
    data = sep.join(sorted(collection))
    if isinstance(collection, set):
        return f'{{{data}}}'
    elif isinstance(collection, list):
        return str(collection)
