from functools import lru_cache

from geo.providers.osrm_module import get_osrm_matrix
from models.rich_vrp.geometries.base import BaseGeometry
from models.rich_vrp.geometries.geometry import DistanceAndTimeMatrixGeometry
from utils.types import Array


class OSRMMatrixGeometry(DistanceAndTimeMatrixGeometry):
    """
    Простая геометрия, которая получает на вход одну матрицу расстояний
    и дефолтную скорость (которую можно менять)
    """

    def __init__(
        self,
        points: Array,
        transport: str,
    ) -> None:

        distances, durations = get_osrm_matrix(points, transport=transport)
        super().__init__(points, distance_matrix=distances, time_matrix=durations)


# class SimpleTransportGeometry(OSRMMatrixGeometry):
