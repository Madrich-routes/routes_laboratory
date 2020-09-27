import abc
from functools import cached_property

import numpy as np

from utils.types import Array


class BaseGeometry(abc.ABC):
    """
    Класс, который инкапсулирует внутри себя всю сложность получения расстояний
    и времен перемещения между точками. Умеет отдавать расстояния и времена перемещения при разных условиях.

    Этот класс должен помочь поддерживать с одинаковым интерфейсом расстояния с пробками,
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

    @cached_property
    def dist_matrix(self, **kwargs) -> Array:
        """
        Дефолтная реализация матрицы расстояния
        """
        return np.array([
            [self.dist(i, j, **kwargs) for i in range(self.size())]
            for j in range(self.size())
        ])

    @cached_property
    def time_matrix(self, **kwargs) -> Array:
        """
        Дефолтная реализация матрицы времени
        """
        return np.array([
            [self.dist(i, j, **kwargs) for i in range(self.size())]
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

        self.dist = dist
        self.mapping = list(range(len(dist)))  # маппинг индекса на индекс в матрице
        self.default_speed = default_speed

    def dist(self, i: int, j: int, **kwargs) -> int:
        pass

    def time(self, i: int, j: int, **kwargs) -> int:
        pass

    @property
    def n(self) -> int:
        return len(self.dist)

    @cached_property
    def time_matrix(self):
        """
        Вообще говоря, это лучше не использовать. Это скорее адаптер.
        """
        return self.dist / self.default_speed

    @cached_property
    def dist_matrix(self):
        return self.dist / self.default_speed
