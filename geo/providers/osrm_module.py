"""
Модуль с утилитами для обращения к OSRM серверу
"""

from itertools import chain
from typing import List, Union, Tuple
from urllib.parse import quote

import numpy as np
import requests
import ujson
from polyline import encode as polyline_encode

import settings
from geo.transforms import geo_distance
from utils.data_formats import cache, is_number
from utils.types import Array

array = np.ndarray
Point = Tuple[float, float]

osrm_host = 'http://osrm-car.dimitrius.keenetic.link'

coefficient = {'speed_car': 7.5, 'speed_pedestrian': 1, 'distance_car': 1.06, 'distance_pedestrian': 0.8}


def _encode_src_dst(src, dst):
    coords = tuple((c[1], c[0]) for c in chain(src, dst))
    polyline = polyline_encode(coords)

    ls, ld = map(len, (src, dst))

    params = dict(
        sources=";".join(map(str, range(ls))),
        dests=";".join(map(str, range(ls, ls + ld))),
        annotations=True,
    )

    return quote(polyline), params


def _encode_src(src):
    coords = tuple((c[1], c[0]) for c in src)
    polyline = polyline_encode(coords)

    params = dict(annotations="duration")

    return quote(polyline), params


def _turn_over(points):
    pts = points.copy()
    for i in range(len(pts)):
        pts[i][0], pts[i][1] = points[i][1], points[i][0]
    return pts


def get_matrix(points: Union[array, List[Point]], factor: Union[str, List[str]], host=osrm_host, dst=None,
               profile="driving") -> Union[array, List[array]]:
    """ Возвращает ассиметричные матрицы смежности
    :param points: points
    :param factor: duration; distance annotation for osrm
    :param host: osrm host
    :param dst:
    :param profile: default 'driving'
    :return: one matrix in case key=str and list of matrix when key=list
    """
    points = points if type(points) == array else to_array(points)
    points = _turn_over(points)
    if dst is not None:
        polyline, _ = _encode_src_dst(points, dst)
    else:
        polyline, _ = _encode_src(points)

    annotation = ','.join(factor) if type(factor) is list else factor
    r = requests.get(f"{host}/table/v1/{profile}/polyline({polyline})?annotations={annotation}")
    assert r.status_code == 200, f'osrm bad request: {r.reason}'
    parsed_json = ujson.loads(r.content)

    if type(factor) is str:
        output = np.array(parsed_json[f'{factor}s'])
        assert output.sum() != 0, 'координаты переверни, да?'
        return output
    else:
        output = [np.array(parsed_json[f'{fact}s']) for fact in factor]
        assert any([m.sum() == 0 for m in output]), 'координаты переверни, да?'
        return output


def get_matrices(points: Union[array, List[Point]], factor: Union[str, List[str]], max_cost: int, split=15,
                 host=osrm_host, dst=None, profile="driving") -> Union[array, List[array]]:
    """ Возвращает нужное кол-во матриц смежностей
    :param points: points
    :param factor: duration, distance
    :param max_cost: сколько времени со старта пройдет
    :param split: минуты
    :param host: osrm host
    :param dst:
    :param profile: default 'driving'
    :return: one matrix of matrix in case key=str and list when key=list
    """
    split *= 60
    size = len(points)
    length = int(np.ceil(max_cost / split))

    result = get_matrix(points, factor, host, dst, profile)
    if type(result) is list:
        output = []
        for res in result:
            matrices = np.zeros(shape=(length, size, size), dtype=np.int64)
            for i in range(length):
                matrices[i] = res.copy()
            output.append(matrices)
    else:
        output = np.zeros(shape=(length, size, size), dtype=np.int64)
        for i in range(length):
            output[i] = result

    return output


def table(host, src, dst=None, profile="driving"):
    """
    Отправляем запрос в OSRM и получаем ответ
    """
    if dst is not None:
        polyline, params = _encode_src_dst(src, dst)
    else:
        polyline, params = _encode_src(src)

    url = f"{host}/table/v1/{profile}/polyline({polyline})?annotations=duration,distance"
    parsed_json = ujson.loads(requests.get(url).content)

    return np.array(parsed_json["distances"], dtype=np.int32), np.array(parsed_json["durations"], dtype=np.int32)


@cache.memoize()
def get_osrm_matrix(
        points: Array,
        dst_points: Array = None,
        transport: str = 'car',
        return_distances: bool = False,
        return_durations: bool = True,
) -> Union[Array, Tuple[Array, Array]]:
    """
    Получаем расстояния.
    """
    assert return_distances or return_durations, 'Ничего не возвращаем'

    print("Не нашли в кеше. Обновляем матрицу расстояний...")

    if transport == 'car':
        osrm_host = f'http://{settings.OSRM_CAR_HOST}:{settings.OSRM_CAR_PORT}'
    elif transport == 'foot':
        osrm_host = f'http://{settings.OSRM_FOOT_HOST}:{settings.OSRM_FOOT_PORT}'
    elif transport == 'bicycle':
        osrm_host = f'http://{settings.OSRM_BICYCLE_HOST}:{settings.OSRM_BICYCLE_PORT}'
    else:
        raise ValueError('Неизвестный транспорт')

    distances, durations = table(
        host=osrm_host,
        src=points,
        dst=dst_points,
    )

    assert np.abs(durations).sum() != 0 and np.abs(distances).sum() != 0, (
        f"OSRM вернул 0 матрицу. Проверьте порядок координат."
        f"{points}"
        f"{durations}"
        f"{distances}"
    )

    # TODO: фиксить матрицу. Оценивать коэффициент прямо тут

    if return_durations and not return_distances:
        return durations
    elif return_distances and not return_durations:
        return distances
    else:
        return distances, durations


def fix_matrix(matrix: np.ndarray, coords: np.ndarray, coeff: float) -> np.ndarray:
    """
    Чиним отсустсвующие значения в матрице расстояния.

    :param matrix: Вычисленная матрица расстояний
    :param coords: Координаты
    :param coeff: Коэффициент отличия расстояний по прямой и не по прямойы
    """
    n = len(matrix)

    for i in range(n):
        for j in range(n):
            if not is_number(matrix[i, j]):
                matrix[i, j] = coeff * geo_distance(coords[i], coords[i])

    return matrix.astype('int32')
