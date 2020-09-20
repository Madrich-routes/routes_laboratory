import numpy as np


class DistanceMatrix:
    def __init__(
            self,
            matrix: np.ndarray
    ) -> None:
        self.matrix = matrix

    def __len__(self) -> int:
        return len(self.matrix)

    def dist(self):
        return self.matrix

    def time(
            self,
            speed: int,
    ):
        return self.matrix / speed
