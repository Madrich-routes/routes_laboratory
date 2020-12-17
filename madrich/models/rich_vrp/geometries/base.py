import abc
import numpy as np
from functools import lru_cache

from madrich.geo.transforms import geo_distance, line_distance_matrix
from madrich.utils.types import Array


class BaseGeometry(abc.ABC):
    """Интерфейс для геометрии — объекта, который умеет отдавать расстояние.

    Геометрия — класс, который инкапсулирует внутри себя всю сложность получения расстояний
    и времен перемещения между точками. Умеет отдавать расстояния и времена перемещения при разных условиях.

    Этот интерфейс должен помочь поддерживать с одинаковым интерфейсом расстояния с пробками,
    разные профили, гетерогенные расстояния, расстояния с динамическими запросами,
    статические матрицы, евклидовы матрицы, etc.
    """

    def __init__(self, points: Array):
        self.points = points

    def size(self):
        """Количество точек в нашей геометриии."""
        return len(self.points)

    @abc.abstractmethod
    def dist(self, i: int, j: int, **kwargs) -> int:
        """Запрос на расстояние принимает индексы точек и что угодно еще."""
        pass

    @abc.abstractmethod
    def time(self, i: int, j: int, **kwargs) -> int:
        """Запрос на время принимает индексы точек и что угодно еще."""
        pass

    def line_dist(self, i, j):
        """Расстояние между точкам по прямой."""
        return geo_distance(self.points[i], self.points[j])

    @lru_cache
    def line_dist_matrix(self, **kwargs):
        """Матрица расстояний между точками."""
        assert len(kwargs) == 0
        return line_distance_matrix(self.points, self.points)

    @lru_cache
    def dist_matrix(self, **kwargs) -> Array:
        """Дефолтная реализация матрицы расстояния."""
        return np.array(
            [
                [self.dist(i, j, **kwargs) for i in range(self.size())]
                for j in range(self.size())
            ]
        )

    @lru_cache
    def time_matrix(self, **kwargs) -> Array:
        """Дефолтная реализация матрицы времени."""
        return np.array(
            [
                [self.time(i, j, **kwargs) for i in range(self.size())]
                for j in range(self.size())
            ]
        )
