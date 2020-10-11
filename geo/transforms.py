"""
В этом модуле описаны различные функции преобразования координат.
Тут не используются классы, только обычные numpy массивы и так далее.
"""
from datetime import datetime
from typing import Tuple, Set

import geopy
import numpy as np
import timezonefinder as tf
from auromat.coordinates.transform import spherical_to_cartesian
from geopy.distance import geodesic
from pytz import timezone, utc
from scipy.spatial import Delaunay
from scipy.spatial.distance import pdist
from scipy.spatial.qhull import ConvexHull
from sklearn.decomposition import PCA
from sklearn.metrics import pairwise_distances
from sklearn.neighbors._dist_metrics import DistanceMetric

from utils.types import Array

EARTH_R = 6373


# TODO: нормальную матрицу расстояний -> 2мерные координаты (картографическая проекция)


def line_distance_matrix(a: Array) -> Array:
    """
    Матрица расстояний по прямой
    """
    return pairwise_distances(a, metric=great_circle_distance)


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
    Превращаем широту и долготу в трехмерные координаты.
    Используем geopy — похоже, что это самое эффективное и точное, что есть.
    Порядок - lat, lon
    """

    return geopy.distance.distance(a, b).m


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
