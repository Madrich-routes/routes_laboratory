"""Это модель, которая создает маппинг объектов Place на BaseGeometry, чтобы можно было считать между ними
расстояние."""
from typing import Iterable, Dict

import numpy as np

from madrich.models.rich_vrp.place import Place


class PlaceMapping:
    """Базовая реализация маппинга точек. Класс хранит внутри себя соотвветствие точек индексам.

    Позволяем получить точки по индексам и наоборот, а также получать время и расстояние между точками.

    Parameters
    ----------
    places : Точки, которые нужно добавить в маппинг
    geometries: наши геометрии в формате Dict[str, Dict[str, np.ndarray]]
    где первой строкой является имя геометрии(driver, pedestrian, bicycle),
    а второй - тип матрицы(dist_matrix, time_matrix)
    """

    def __init__(self, places: Iterable[Place], geometries: Dict[str, Dict[str, np.ndarray]]):
        self.places = places
        self.geometries = geometries
        self.points = np.array([[place.lat, place.lon] for place in self.places])

        self.places_to_indexes = {place: i for i, place in enumerate(places)}
        self.indexes_to_places = {i: place for i, place in enumerate(places)}

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

        return self.indexes_to_places[i]

    def index(self, p: Place) -> int:
        """Получаем индекс по точке.

        Parameters
        ----------
        p : Точка

        Returns
        -------
        Ее индекс в маппинге
        """

        return self.places_to_indexes[p]

    def dist(self, p1: Place, p2: Place, profile: str) -> int:
        """Посчитать расстояние.

        Parameters
        ----------
        p1 : Место старта
        p2 : Место финиша
        profile : Профайл, для которого мы считаем результат

        Returns
        -------
        Расстояние
        """
        i1, i2 = self.places_to_indexes[p1], self.places_to_indexes[p2]
        return self.geometries[profile]["dist_matrix"][i1, i2]

    def time(self, p1: Place, p2: Place, profile: str) -> int:
        """Посчитать время.

        Parameters
        ----------
        p1 : Место старта
        p2 : Место финиша
        profile : Профайл, для которого мы считаем результат

        Returns
        -------
        Время
        """
        i1, i2 = self.places_to_indexes[p1], self.places_to_indexes[p2]
        return self.geometries[profile]["time_matrix"][i1, i2]
