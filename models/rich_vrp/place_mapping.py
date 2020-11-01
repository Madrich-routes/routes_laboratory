"""
Это модель, которая создает маппинг объектов Place на BaseGeometry, чтобы можно было считать между ними расстояние
"""
from abc import ABC
from typing import Iterable

from models.rich_vrp import Place
from models.rich_vrp.geometry import BaseGeometry
from temp.tsp import List


class BasePlaceMapping(ABC):
    def __init__(
        self,
        places: Iterable[Place],
        geometry_class: BaseGeometry,
    ):
        self.places = places
        self.geometry_class = geometry_class

    def dist(self):
        rai
