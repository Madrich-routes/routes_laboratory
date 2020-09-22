from collections import defaultdict
from functools import cached_property

import numpy as np

# TODO: возможно, все же, этих дистанс-матриц нужно очень много

class DistanceMatrix:
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

    # def dist(self, i: int, j: int):
    #     return self.dist

    # def time(self, i: int, j: int):
    #     return self.dist
