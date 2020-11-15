"""Модуль с утилитами для обращения к OSRM серверу."""
import urllib
from itertools import chain
from typing import Optional, Tuple
from urllib.parse import quote

import numpy as np
import requests
from fastcore.basics import null, ifnone
from polyline import encode as polyline_encode

import settings
from geo.transforms import line_distance_matrix
from utils.data_formats import cache
from utils.logs import logger
from utils.types import Array


def get_osrm_matrix(
    src: Array,
    dst: Optional[Array] = None,
    *,
    transport: str = 'car',
    profile: str = 'driving',
    return_distances: bool = True,
    return_durations: bool = True,
    fix_matrix: bool = True,
) -> Tuple[Optional[Array], Optional[Array]]:
    """Получаем матрицу расстояний.

    Матрица от src до dst, или от src до src, если dst не указан.
    Эта функция является "фронтендом", она обрабатывает параметры, обеспечивает удобный интерфейс,
    вызывает исправление решения и так далее.
    Всю остальную работу эта функция передает функции table.

    TODO: Добавить фиксы для каждого профайла
    TODO: Добавить distance matrix missing value imputing (Вычисление из структуры матрицы)
    TODO: Добавить корректироваки, возможно в отдельную геометрию
        {'speed_car': 7.5, 'speed_pedestrian': 1, 'distance_car': 1.06, 'distance_pedestrian': 0.8}

    Parameters
    ----------
    src : Набор точек, из которых мы считаем расстояния
    dst : Набор точек до куда считаем расстояния. Если None, то считаем (src, src)
    transport : {'car', 'foot', 'bicycle'} Тип транспорта, профайл
    profile : TODO: Не знаю, что это. Но osrm это принимает.
    return_distances : Возвращать ли расстояния
    return_durations : Возвращать ли время
    fix_matrix : Исправлять ли кривые значения в матрице

    Returns
    -------
    Возвращаемся матрицу расстояния и/или времени
    """
    assert len(src) != 0, 'Не заданы начальные точки'
    assert dst is None or len(dst) != 0, 'Не заданы конечные точки'
    assert return_distances or return_durations, 'Ничего не возвращаем'

    src = np.array(src, dtype=np.float32)
    dst = dst if dst is None else np.array(dst, dtype=np.float32)

    host = dict(  # выбираем сервер, к которому обращаемся
        car=f'http://{settings.OSRM_CAR_HOST}:{settings.OSRM_CAR_PORT}',
        foot=f'http://{settings.OSRM_FOOT_HOST}:{settings.OSRM_FOOT_PORT}',
        bicycle=f'http://{settings.OSRM_BICYCLE_HOST}:{settings.OSRM_BICYCLE_PORT}',
    )[transport]

    logger.info(f"Ищем в кеше матрицу расстояний...")
    distances, durations = _table(
        host=host,
        src=src,
        dst=dst,
        profile=profile,
        return_distances=return_distances,
        return_durations=return_durations,
    )

    assert (  # проверяем, что матрица не нулевая
        (durations is None or np.abs(durations).sum() != 0)
        and (distances is None or np.abs(distances).sum() != 0)
    ), (
        f"OSRM вернул 0 матрицу. Проверьте порядок координат."
        f"{src}"
        f"{durations}"
        f"{distances}"
    )

    # заменяем сомнительные значения, на что-то похожее на правду
    if fix_matrix and (return_distances + return_durations) == 2:
        distances, durations = _fix_matrix(distances, durations, src, dst)
    else:
        logger.debug("Не фиксим матрицы")

    return distances, durations


def _encode_src_dst(
    src: Array,
    dst: Optional[Array] = None,
    *,
    return_distances: bool = True,
    return_durations: bool = True,
) -> Tuple[str, str]:
    """Кодируем координаты src, dst в виде параетров.

    Parameters
    ----------
    src : Набор точек источников
    dst : Набор точек финишей
    return_distances : Возвращать ли расстояния
    return_durations : Возвращаться ли время

    Returns
    -------
    Закодированный polyline и закодированные params для подстановки в url
    """

    coords = src if dst is None else np.vstack([src, dst])
    # _turn_over(np.array(coords))
    polyline = polyline_encode(coords)

    params = {
        'annotations': ','.join(
            ['duration'] * return_durations
            + ['distance'] * return_distances
        )
    }
    if dst is not None:
        ls, ld = map(len, (src, dst))
        params['sources'] = ";".join(map(str, range(ls)))
        params['destinations'] = ";".join(map(str, range(ls, ls + ld)))

    return urllib.parse.quote(polyline), urllib.parse.urlencode(params)


# @cache.memoize()
def _table(
    host: str,
    src: Array,
    dst: Optional[Array] = None,
    profile: str = "driving",
    return_distances: bool = False,  # что мы хотим получить в результате
    return_durations: bool = True,
) -> Tuple[Array, Array]:
    """Отправляем запрос матрицы расстояний в OSRM и получаем ответ

    Матрица с одинаковыми параметрами кешируется при первом вызове.

    Parameters
    ----------
    host : Инстанс OSRM, который мы проверяем
    src : np.array точек, от которых мы считаем расстояние
    dst : np.array точек, до которых мы считаем расстояние
    profile : Какой-то параметр osrm

    return_distances : Возвращать ли расстояния
    return_durations : Возвращать ли время перемещения
    """
    polyline, params = _encode_src_dst(
        src, dst,
        return_distances=return_distances,
        return_durations=return_durations
    )
    url = f"{host}/table/v1/{profile}/polyline({polyline})?{params}"

    dst_len = len(dst) if dst is not None else None
    logger.info(f"Не нашли в кеше. Обновляем матрицу расстояний... {len(src), dst_len}")

    r = null
    try:  # делаем запрос с обработкой ошибок
        r = requests.get(url)
        r.raise_for_status()
    except Exception as e:
        logger.error(f'Проблема: {r.content}')
        raise e

    logger.info(f'{r.elapsed} затрачно на вычисление матрицы.')

    parsed_json = r.json()

    di, du = parsed_json.get("distances"), parsed_json.get("durations")
    return (
        np.array(di, dtype=np.int32) if di is not None else None,
        np.array(du, dtype=np.int32) if du is not None else None,
    )


def _fix_matrix(
    distances: Array,
    durations: Array,
    src: Array,
    dst: Array,
    speed_ratio_low_threshold: float = 2,
    speed_ratio_up_threshold: float = 1.5,
) -> Array:
    """Чиним отсустсвующие и неправильные значения в матрице расстояний.

    Постусловия:
    1. Нет отсутствующих, и заведомо неверных значений
    2. Скорости не отличаются слишком сильно от средней скорости

    Parameters
    ----------
    distances : Матрица расстояний
    durations : Матрица времени
    src : Точки из которых едем
    dst : Точки в которые едем
    speed_ratio_low_threshold : Во сколько раз скорость может быть меньше средней
    speed_ratio_up_threshold : Во сколько раз скорость может быть больше средней

    Returns
    -------
    Исправленная матрица
    """
    line_matrix = line_distance_matrix(src, dst)  # считаем расстояния по прямой

    # заменяем мусорные значения на 0
    distances[(distances < 0) | (distances > 1e7) | ~np.isfinite(distances)] = 0
    durations[(durations < 0) | (durations > 1e7) | ~np.isfinite(durations)] = 0

    if (
        (distances == 0).sum() > distances.size * 0.1
        or (durations == 0).sum() > durations.size * 0.1
    ):
        logger.warning('Более 10% нулевых или неверных значений в матрице расстояний!!!')

    # заполняем нулевые расстояния
    di_sum = distances[durations != 0].sum()  # считаем сумму там, где нет 0
    l_sum = line_matrix[(distances != 0) & (durations != 0)].sum()
    l_di_coeff = di_sum / l_sum
    distances[distances == 0] = l_di_coeff * line_matrix[distances == 0]

    # заполняем нулевое время
    du_sum = durations[distances != 0].sum()
    di_sum = distances[durations != 0].sum()
    avg_speed = di_sum / du_sum
    durations[durations == 0] = distances[durations == 0] / avg_speed

    # заменяем время там, где скорости выглядять сомнительно
    speeds = distances / (durations + 1e-10)
    speeds = speeds.clip(avg_speed / speed_ratio_low_threshold, avg_speed * speed_ratio_up_threshold)
    durations = distances / (speeds + 1e-10)

    return distances.astype('int32'), durations.astype('int32')


def _turn_over(points: Array) -> Array:
    """Переворачиваем координаты, (lat, lon) -> (lon, lat) или наоборот.

    Parameters
    ----------
    points : np.array с коордиантами точке

    Returns
    -------
    Массив с перевернутыми координатами точек
    """
    return np.fliplr(points)
