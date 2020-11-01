"""
В этом модуле описаны различные функции преобразования координат.
Тут не используются классы, только обычные numpy массивы и так далее.
"""
import math
from datetime import datetime
from typing import Optional, Set, Tuple

import geopy
import numpy as np
import timezonefinder as tf
from auromat.coordinates.transform import spherical_to_cartesian
from geopy.distance import geodesic
from numba import njit
from pytz import timezone, utc
from scipy.spatial import Delaunay
from scipy.spatial.qhull import ConvexHull
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import haversine_distances
from sklearn.neighbors._dist_metrics import DistanceMetric

from utils.types import Array

EARTH_R = 6371.0087714150598


# TODO: нормальную матрицу расстояний -> 2мерные координаты (картографическая проекция)


def line_distance_matrix(a: Array, b: Optional[Array] = None) -> Array:
    """
    Матрица расстояний по прямой
    """
    # TODO: try https://github.com/mapado/haversine
    # return pairwise_distances(a, metric=great_circle_distance)  # этот способ медленнее
    return haversine_distances(a, b)


def sklearn_haversine(a, b):
    """
    Вычисляем с использованием sklearn
    :param a:
    :param b:
    :return:
    """
    dist = DistanceMetric.get_metric('haversine')
    lat_a, lat_b = a[:, 0], b[:, 0]
    lon_a, lon_b = a[:, 1], b[:, 1]

    X = [[np.radians(lat_a), np.radians(lon_b)], [np.radians(lat_a), np.radians(lon_b)]]
    return EARTH_R * dist.pairwise(X)


def great_circle_distance(a, b):
    """
    Расстояние по большой окружности
    """
    return geopy.distance.great_circle(a, b).m


def geo_distance(a: Array, b: Array):
    """
    Вычисляем точное, но медленное расстояние по прямой по земле
    """

    return geopy.distance.distance(a, b).m


def haversine_vectorize(lon1, lat1, lon2, lat2):
    """
    Векторизованная версия haversine
    """
    EARTH_R = 6371.0087714150598

    lon1, lat1, lon2, lat2 = np.radians(lon1), np.radians(lat1), np.radians(lon2), np.radians(lat2)

    newlon = lon2 - lon1
    newlat = lat2 - lat1

    haver_formula = np.sin(newlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(newlon / 2.0) ** 2

    dist = 2 * np.arcsin(np.sqrt(haver_formula))
    km = EARTH_R * dist
    return km


@njit()
def haversine_numba(a, b):
    """
    Версия расстояния, оптимизированная numba
    """
    s_lat, s_lon = a
    e_lat, s_lon = b

    R = 6373.0
    s_lat = s_lat * math.pi / 180
    s_lng = s_lon * math.pi / 180
    e_lat = e_lat * math.pi / 180
    e_lng = s_lon * math.pi / 180
    d = math.sin((e_lat - s_lat) / 2) ** 2 + \
        math.cos(s_lat) * math.cos(e_lat) * \
        math.sin((e_lng - s_lng) / 2) ** 2
    return 2 * R * math.asin(math.sqrt(d)) * 1000


def geo_to_3d(lat, lon) -> Tuple[float, float, float]:
    """
    Получаем 3D координаты точки
    """
    return spherical_to_cartesian(EARTH_R, lat, lon)


def make_flat(points: np.ndarray) -> np.ndarray:
    """
    Преобразуем массив трехмерных точек к двумерному с сохранением расстояний
    TODO: utm, pyproj
    https://gis.stackexchange.com/questions/212723/how-can-i-convert-lon-lat-coordinates-to-x-y
    """
    return PCA(n_components=2).fit_transform(points)


def delaunay_graph(points: np.ndarray) -> Set[Tuple[int, int]]:
    """
    Вычисляет граф делоне

    :param points: Множество точек в 2D (np.array).
    :return: Множество ребер в виде пар индексов точек
    """
    assert len(points[0]) == 2, "Координаты должны быть двумерными"

    tri = Delaunay(points)

    res = set()
    for s in tri.simplices:
        s.sort()
        res.add((s[0], s[1]))
        res.add((s[0], s[2]))
        res.add((s[1], s[3]))

    return res


def distance_matrix(src: np.ndarray, dst: np.ndarray, method=geo_distance) -> np.ndarray:
    """
    src, dst: Lists of coords (lat, lon)
    Возвращаем матрицу расстояний по прямой
    """
    for a in src:
        for b in dst:
            ...


class DynamicConvexHull:
    """
    TODO: Оптимизировать по размеру выпуклой оболочки
    """

    def __init__(self, points: np.ndarray):
        self.hull = ConvexHull(points, incremental=True)

    def volume(self):
        """
        Площадь внутри
        """
        return self.hull.volume

    def area(self):
        """
        :return: Площадь поверхности
        """
        return self.hull.area


def get_offset(*, lat, lng):
    """
    Смещение от UTC в часах
    """
    today = datetime.now()
    tz_target = timezone(tf.certain_timezone_at(lng=lng, lat=lat))

    # TODO: ATTENTION: tz_target could be None! handle error case
    today_target = tz_target.localize(today)
    today_utc = utc.localize(today)
    return (today_utc - today_target).total_seconds() / 3600
