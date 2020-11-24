"""В этом модуле описаны различные функции преобразования координат.

Тут не используются классы, только обычные numpy массивы и так далее.
"""
from datetime import datetime
from typing import Optional, Set, Tuple

import geopy
import numpy as np
import timezonefinder as tf
from geopy.distance import geodesic
from pytz import timezone, utc
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import haversine_distances
from sklearn.neighbors._dist_metrics import DistanceMetric  # noqa

from madrich.utils.types import Array

EARTH_R = 6371.0087714150598


# TODO: нормальную матрицу расстояний -> 2мерные координаты (картографическая проекция)


def line_distance_matrix(a: Array, b: Optional[Array] = None) -> Array:
    """Матрица расстояний по прямой.

    Максимально быстраа реализация из опробованных.
    """
    # TODO: try https://github.com/mapado/haversine
    # return pairwise_distances(a, metric=great_circle_distance)  # этот способ медленнее
    return haversine_distances(a, b)


def great_circle_distance(a, b):
    """Расстояние по большой окружности."""
    return geopy.distance.great_circle(a, b).m


def geo_distance(a: Array, b: Array):
    """Вычисляем точное, но медленное расстояние по прямой по земле."""

    return geopy.distance.distance(a, b).m


def extract_coords(
    dist: np.ndarray,
    k=2,
):
    """Извлекаем 2d координаты точек по матрице расстояний

    dist: матрица расстояний
    k: размерность пространства в котором хотим получить координаты
    """
    M = (dist[0, :] ** 2 + dist[:, 0].reshape(-1, 1) ** 2 - dist ** 2) / 2  # матрица грамма

    S, U = np.linalg.eig(M)  # разложение на собственные векторы
    S, U = np.real(S), np.real(U)  # откидываем мнимую часть
    S[np.isclose(S, 0)] = 0  # отсекаем близкие к 0 (они потом отрицательными становятся)
    S = np.sqrt(S)  # Берем корень собственных значений

    idx = np.argpartition(-S, k)[:k]  # индексы k наибольших собственных значений
    coords = U @ np.diag(S)  # а вот и коордианты. Нужное нам будет в колонках idx

    return coords[:, idx]


def geo_to_3d(lat, lon) -> Tuple[float, float, float]:
    """Получаем 3D координаты точки."""
    from auromat.coordinates.transform import spherical_to_cartesian

    return spherical_to_cartesian(EARTH_R, lat, lon)


def make_flat(points: np.ndarray) -> np.ndarray:
    """
    Преобразуем массив трехмерных точек к двумерному с сохранением расстояний
    TODO: utm, pyproj
    https://gis.stackexchange.com/questions/212723/how-can-i-convert-lon-lat-coordinates-to-x-y
    """
    return PCA(n_components=2).fit_transform(points)


def delaunay_graph(points: np.ndarray) -> Set[Tuple[int, int]]:
    """Вычисляет граф делоне.

    :param points: Множество точек в 2D (np.array).
    :return: Множество ребер в виде пар индексов точек
    """
    from scipy.spatial import Delaunay  # noqa

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
        from scipy.spatial.qhull import ConvexHull  # noqa

        self.hull = ConvexHull(points, incremental=True)

    def volume(self):
        """Площадь внутри."""
        return self.hull.volume

    def area(self):
        """
        :return: Площадь поверхности
        """
        return self.hull.area


def get_offset(*, lat, lng):
    """Смещение от UTC в часах."""
    today = datetime.now()
    tz_target = timezone(tf.certain_timezone_at(lng=lng, lat=lat))

    # TODO: ATTENTION: tz_target could be None! handle error case
    today_target = tz_target.localize(today)
    today_utc = utc.localize(today)
    return (today_utc - today_target).total_seconds() / 3600
