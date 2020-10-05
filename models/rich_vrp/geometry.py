"""
В этом модуле находятся разные геометрии. Штуковины, которые отдают
 расстояние и время проезда в зависимости от условий.
"""

import abc
from functools import lru_cache

import numpy as np
import scipy

from geo.transforms import geo_distance, haversine_matrix
from utils.types import Array


class BaseGeometry(abc.ABC):
    """
    Интерфейс для геометрии — объекта, который умеет отдавать расстояние.

    Геометрия — класс, который инкапсулирует внутри себя всю сложность получения расстояний
    и времен перемещения между точками. Умеет отдавать расстояния и времена перемещения при разных условиях.

    Этот интерфейс должен помочь поддерживать с одинаковым интерфейсом расстояния с пробками,
    разные профили, гетерогенные расстояния, расстояния с динамическими запросами,
    статические матрицы, евклидовы матрицы, etc.
    """

    def __init__(
            self,
            points: Array
    ):
        self.points = points

    def size(self):
        """
        Количество точек в нашей геометриии
        """
        return len(self.points)

    @abc.abstractmethod
    def dist(self, i: int, j: int, **kwargs) -> int:
        """
        Запрос на расстояние принимает индексы точек и что угодно еще
        """
        pass

    @abc.abstractmethod
    def time(self, i: int, j: int, **kwargs) -> int:
        """
        Запрос на время принимает индексы точек и что угодно еще
        """
        pass

    def line_dist(self, i, j):
        """
        Расстояние между точкам по прямой
        """
        return geo_distance(self.points[i], self.points[j]).m

    @lru_cache
    def line_dist_matrix(self, **kwargs):
        """
        Матрица расстояний между точками
        """
        assert len(kwargs) == 0
        return haversine_matrix(self.points, self.points)

    @lru_cache
    def dist_matrix(self, **kwargs) -> Array:
        """
        Дефолтная реализация матрицы расстояния
        """
        return np.array([
            [self.dist(i, j, **kwargs) for i in range(self.size())]
            for j in range(self.size())
        ])

    @lru_cache
    def time_matrix(self, **kwargs) -> Array:
        """
        Дефолтная реализация матрицы времени
        """
        return np.array([
            [self.time(i, j, **kwargs) for i in range(self.size())]
            for j in range(self.size())
        ])


class DistanceMatrixGeometry(BaseGeometry):
    """
    Простая геометрия, которая получает на вход одну матрицу расстояний
    и дефолтную скорость (которую можно менять)
    """

    def __init__(
            self,
            points: Array,
            distance_matrix: Array,
            default_speed: float,
    ) -> None:
        super().__init__(points)

        self.d = distance_matrix  # расстояния
        self.default_speed = default_speed  # скорость в метрах в секунду

    def dist(self, i: int, j: int, **kwargs) -> int:
        return self.d[i, j]

    def time(self, i: int, j: int, **kwargs) -> int:
        speed = kwargs.get("speed", self.default_speed)
        return self.d[i, j] / speed

    @lru_cache
    def time_matrix(self, **kwargs):
        """
        Вообще говоря, это лучше не использовать. Это скорее адаптер.
        """
        assert len(kwargs) == 0
        return self.d / self.default_speed

    @lru_cache
    def dist_matrix(self, **kwargs):
        assert len(kwargs) < 1
        speed = kwargs.get("speed", self.default_speed)
        return self.d / speed


class DistanceAndTimeMatrixGeometry(BaseGeometry):
    """
    Геометрия, которой задали 2 матрицы — времени и расстояния
    """

    def __init__(
            self,
            points: Array,
            distance_matrix: Array,
            time_matrix: Array,
    ) -> None:
        super().__init__(points)

        self.d = distance_matrix
        self.t = time_matrix

    def dist(self, i: int, j: int, **kwargs) -> int:
        return self.d[i, j]

    def time(self, i: int, j: int, **kwargs) -> int:
        return self.t[i, j]

    @lru_cache
    def time_matrix(self, **kwargs):
        """
        Вообще говоря, это лучше не использовать. Это скорее адаптер.
        """
        assert len(kwargs) == 0
        return self.d

    @lru_cache
    def dist_matrix(self, **kwargs):
        return self.t


class HaversineGeometry(BaseGeometry):
    """
    Геометрия, которая считает расстояние напрямую между точками, заданными lat и lon
    """

    def __init__(
            self,
            points: Array,
            default_speed: float,
    ) -> None:
        super().__init__(points)
        self.default_speed = default_speed

    @lru_cache
    def dist(self, i: int, j: int, **kwargs) -> int:
        assert len(kwargs) == 0
        self.line_dist(i, j)

    @lru_cache
    def time(self, i: int, j: int, **kwargs) -> int:
        assert len(kwargs) < 1
        speed = kwargs.get("speed", self.default_speed)
        return self.dist(i, j) / speed

    @lru_cache
    def dist_matrix(self, **kwargs):
        assert len(kwargs) == 0
        return self.line_dist_matrix()

    @lru_cache
    def time_matrix(self, **kwargs):
        assert len(kwargs) < 1
        speed = kwargs.get("speed", self.default_speed)
        return self.dist_matrix() / speed


class DescartesGeometry(BaseGeometry):
    """
    Геометрия, которая считает расстояние напрямую между точками, заданными декартовыми координаитами
    """

    def __init__(
            self,
            points: Array,
            default_speed: float,
    ) -> None:
        super().__init__(points)
        self.default_speed = default_speed

    @lru_cache
    def dist(self, i: int, j: int, **kwargs) -> int:
        return np.linalg.norm(self.points[i] - self.points[j])

    @lru_cache
    def time(self, i: int, j: int, **kwargs) -> int:
        assert len(kwargs) < 1
        speed = kwargs.get("speed", self.default_speed)
        return self.dist(i, j) / speed

    @lru_cache
    def dist_matrix(self, **kwargs):
        assert len(kwargs) == 0
        return scipy.spatial.distance_matrix(self.points, self.points)

    @lru_cache
    def time_matrix(self, **kwargs):
        assert len(kwargs) < 1
        speed = kwargs.get("speed", self.default_speed)
        return self.dist_matrix() / speed
