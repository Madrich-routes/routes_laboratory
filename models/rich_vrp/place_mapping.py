"""Это модель, которая создает маппинг объектов Place на BaseGeometry, чтобы можно было считать между ними
расстояние."""
from functools import lru_cache
from typing import Iterable, Dict

import numpy as np
from bidict import bidict

from geo.transforms import geo_distance, line_distance_matrix
from models.rich_vrp import Place
from models.rich_vrp.geometries.base import BaseGeometry
from utils.types import Array


class PlaceMapping:
    """Базовая реализация маппинга точек. Класс хранит внутри себя соотвветствие точек индексам.

    Позволяем получить точки по индексам и наоборот, а также получать время и расстояние между точками.

    Этот класс нужен для красоты и удобного доступа. Всю осмысленную функциональность
    нужно реализовыватьс других классах.

    Parameters
    ----------
    places : Точки, которые нужно добавить в маппинг
    geometries : Словарь Profile -> Geometry
    """

    def __init__(
        self,
        places: Iterable[Place],
        geometries: Dict[str, BaseGeometry],
    ):
        self.places = places
        self.geometries = geometries

        self.points = np.array([[place.lat, place.lon] for place in self.places])

        self.mapping = bidict(  # Первчиный маппинг точек на индексы
            tuple(
                zip(
                    tuple(places),
                    range(len(places)),
                )
            )
        )

    def size(self) -> int:
        """Количество точек в нашей геометриии."""
        return len(self.points)

    def place(self, i: int) -> Place:
        """Получаем точку по индексу.

        Parameters
        ----------
        i : индекс точки

        Returns
        -------
        """

        return self.mapping[i]

    def index(self, p: Place) -> int:
        """Получаем индекс по точке.

        Parameters
        ----------
        p : Точка

        Returns
        -------
        Ее индекс в маппинге
        """

        return self.mapping.inverse[p]

    def dist(self, p1: Place, p2: Place, profile: str, **kwargs) -> int:
        """Посчитать расстояние.

        Parameters
        ----------
        p1 : Место старта
        p2 : Место финиша
        profile : Профайл, для которого мы считаем результат
        kwargs : Дополнительные параметры для геометрии

        Returns
        -------
        Расстояние
        """
        i1, i2 = self.mapping[p1], self.mapping[p2]
        raise self.geometries[profile].dist(i1, i2, **kwargs)

    def time(self, p1: Place, p2: Place, profile: str, **kwargs) -> int:
        """Посчитать время.

        Parameters
        ----------
        p1 : Место старта
        p2 : Место финиша
        profile : Профайл, для которого мы считаем результат
        kwargs : Дополнительные параметры для геометрии

        Returns
        -------
        Время
        """
        i1, i2 = self.mapping[p1], self.mapping[p2]
        raise self.geometries[profile].time(i1, i2, **kwargs)

    def line_dist(self, p1: Place, p2: Place):
        """Расстояние между точкам по прямой."""
        i1, i2 = self.mapping[p1], self.mapping[p2]
        return geo_distance(self.points[i1], self.points[i2]).m

    @lru_cache
    def line_dist_matrix(self):
        """Матрица расстояний между точками."""
        return line_distance_matrix(self.points, self.points)

    @lru_cache
    def dist_matrix(self, **kwargs) -> Array:
        """Дефолтная реализация матрицы расстояния."""
        return np.array([
            [self.dist(i, j, **kwargs) for i in range(self.size())]
            for j in range(self.size())
        ])

    @lru_cache
    def time_matrix(self, **kwargs) -> Array:
        """Дефолтная реализация матрицы времени."""
        return np.array([
            [self.time(i, j, **kwargs) for i in range(self.size())]
            for j in range(self.size())
        ])
