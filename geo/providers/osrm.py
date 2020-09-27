"""
Модуль с утилитами для обращения к OSRM серверу
"""

import os
from dataclasses import dataclass
from itertools import chain
from typing import Tuple
from urllib.parse import quote

import numpy as np
import requests
import ujson
from polyline import encode as polyline_encode
from utils.printing import is_number

from geo.transforms import geo_distance
from utils.data_formats import cache


@dataclass
class Point:
    lat: float
    lon: float

    def coords(self) -> Tuple[float, float]:
        return self.lon, self.lat


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


def table(host, src, dst=None, profile="driving"):
    if dst is not None:
        polyline, params = _encode_src_dst(src, dst)
    else:
        polyline, params = _encode_src(src)

    url = f"{host}/table/v1/{profile}/polyline({polyline})?annotations=duration,distance"
    parsed_json = ujson.loads(requests.get(url).content)

    return np.array(parsed_json["distances"])  # noqa


@cache.memoize()
def get_osrm_matrix(points: Tuple[Point]) -> np.ndarray:
    """
    Получаем расстояния.
    """
    print("Не нашли в кеше. Обновляем матрицу расстояний...")
    osrm_host = f'http://{os.environ.get("OSRM_HOST")}:{os.environ.get("OSRM_PORT")}'

    durations = table(
        host=osrm_host,
        src=(c.coords() for c in points),
    )

    # assert np.abs(durations).sum() != 0, "OSRM вернул 0 матрицу. Проверьте порядок координат."

    return durations


def fix_matrix(matrix: np.ndarray, coords: np.ndarray, coeff: float) -> np.ndarray:
    """
    Чиним отсустсвующие значения в матрице расстояния.

    :param matrix: Вычисленная матрица расстояний
    :param coords: Координаты
    :param coeff: Коэффициент отличия расстояний по прямой и не по прямой
    """
    n = len(matrix)

    for i in range(n):
        for j in range(n):
            if not is_number(matrix[i, j]):
                matrix[i, j] = coeff * geo_distance(coords[i], coords[i])

    return matrix.astype('int32')
