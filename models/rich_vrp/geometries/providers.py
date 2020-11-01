from functools import lru_cache

from models.rich_vrp.geometries.base import BaseGeometry
from utils.types import Array


class OSRMMatrixGeometry(BaseGeometry):
    """
    Простая геометрия, которая получает на вход одну матрицу расстояний
    и дефолтную скорость (которую можно менять)
    """

    def __init__(
        self,
        points: Array,
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
