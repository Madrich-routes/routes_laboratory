"""
В этом модуле описаны различные функции преобразования координат.
Тут не используются классы, только обычные numpy массивы и так далее.
"""
import math
from typing import Tuple, Set

from auromat.coordinates.transform import spherical_to_cartesian
from scipy.spatial import Delaunay
import numpy as np
from scipy.spatial.qhull import ConvexHull
from sklearn.decomposition import PCA
from geopy.distance import geodesic
import geopy
from datetime import datetime
from pytz import timezone, utc
import timezonefinder as tf

EARTH_R = 6373.0


# TODO: нормальную матрицу расстояний -> 2мерные координаты

def geo_distance(lat_a, lon_a, lat_b, lon_b):
    """
    Превращаем широту и долготу в трехмерные координаты.
    Используем geopy — похоже, что это самое эффективное и точное, что есть
    """
    return geopy.distance.distance((lat_a, lon_a), (lat_b, lon_b)).m


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
