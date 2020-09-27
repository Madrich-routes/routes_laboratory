from functools import cached_property

import numpy as np


# TODO: Возможно, все же, этих дистанс-матриц нужно очень много
# TODO: Для графа все же создать именно матрицу расстояний им методы для работы с ней
# TODO: Так же мб матрицу можно создать в структурах данных, чтобы описать маппинг


class Geometry:
    """

    """

    def __init__(
            self,
            dist: np.ndarray,
            speed: float,

    ) -> None:
        self.dist = dist
        self.mapping = list(range(len(dist)))  # маппинг индекса на индекс в матрице
        self.speed = speed

    @property
    def n(self) -> int:
        return len(self.dist)

    @cached_property
    def time_matrix(self):
        return self.dist / self.speed

    @cached_property
    def distance_matrix(self):
        return self.dist / self.speed

    # def dist(self, i: int, j: int):
    #     return self.dist

    # def time(self, i: int, j: int):
    #     return self.dist
