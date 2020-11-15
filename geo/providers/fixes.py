"""Тут расположены разлиные исправления данных, которые мы получаем от провайдера."""
from typing import Tuple, Dict

from geo.settings import FOOT_SPEEDS


def _fix_speed_unknown(
    time: int,
    distance: int,
    speed_limits_dict: Dict[str, float],
    trust_speed_coeff: float,
    mode: str,
):
    """
    Чиним скорость, когда ни скорость ни время не выбиваются из статистики

    Parameters
    ----------
    time : Время
    distance : Расстояние
    speed_limits_dict : Статистики скорости
    trust_speed_coeff : ,
    mode : {'min', 'max'}
    Returns
    -------
    Исправленное время и расстояние
    """

    time_avg = distance / speed_limits_dict["avg"]
    dist_avg = time * speed_limits_dict["avg"]

    if




def _fix_speed(
    time: int,
    distance: int,
    speed_limits_dict: Dict[str, float],
    trust_speed_coeff: float = 0.5,
    max_time: int = 3600,
    max_distance: int = 1e5,
):
    """ Нормализуем время и расстояние таким образом,
     чтобы скорость была нормальной и не было неадекватных занчений.

    Если назкая скорость и время больше одного часа, то пересчитываем через расстояние и среднюю скорость
    Если высокая скорость и расстояние больше 100км, то пересчитываем через время и средню скорость
    Иначе делаем скорость, смещенную к тому, что было через trust_speed_coeff.
    Меняем и время и расстояние

    Parameters
    ----------
    time : Время перемещения
    distance : Расстояние
    speed_limits_dict : Словарь со статистикой по скоростям для данного вида транспорта.
    Должен включать в себя ключи "min", "max", "avg"
    trust_speed_coeff: насколько мы доверяем, что скорость должна быть такой какая есть [0, 1].
     При 0 буедет avg_speed, при 1 будет max_speed
    max_time: максимальное время, которое мы считаем нормальным
    max_distance: максимальное расстояние, которое мы считаем нормальным

    Returns
    -------
    Исправленные время и расстояние
    """
    time = max(time, 0)
    distance = max(distance, 0)

    if time == 0: # исправляем time, если он 0
        return distance / speed_limits_dict['avg'], distance

    speed = distance / time

    if speed < speed_limits_dict["min"]:
        if time > max_time:
            # низкая скорость из-за большого времени
            return distance / speed_limits_dict['avg'], distance
        else:

            return
    elif speed > speed_limits_dict["max"]:
        if distance > max_distance:
            # выская скорость из-за большого расстояния
            return time, time * speed_limits_dict['avg']
        else:
            # просто высокая скорость
            return
    else:
        # все хорошо, возвращаем как есть
        return time, distance





def fix_foot_speed(
    time: int,
    dist: int,
):
    """ Исправляем кривую скорость пешехода

    Parameters
    ----------
    time : время в секундах
    dist : расстояние

    Returns
    -------
    Исправленное время и расстояние
    """

    _fix_speed(time=time, distance=dist, speed_limits_dict=FOOT_SPEEDS)

def fix_driver_speed(
        time: int,
        dist: int
) -> Tuple[int, int]:
    """Исправляем неправдоподобную скорость водителя.

    Parameters
    ----------
    time : время в секундах
    dist : расстояние
    Returns
    -------
    Исправленное время и расстояние
    """
    if time == 0 and dist != 0:

    if time != 0 and 5 < dist / time < 13:
        if time > 3600 or dist <= 1e5:
            return dist // 12, dist
        else:
            return time, time * 12
    return time, dist


def fix_bicycle_speed(
        t: int,
        d: int
) -> Tuple[int, int]:
    """Исправляем неправдоподобную скорость перемещения водителяы.

    Parameters
    ----------
    t : время в секундах
    d : расстояние

    Returns исправленное время и расстояние
    -------
    """
    if t != 0 and 2 < d / t < 5:
        if t > 2 * 60 * 60 or d <= 100 * 1000:
            return d // 4, d
        else:
            return t, t * 4
    return t, d
