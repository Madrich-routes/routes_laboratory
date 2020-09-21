import numpy as np

from models.graph.distance_matrix import DistanceMatrix


def array_gcd(numbers: np.ndarray) -> None:
    res = np.gcd(numbers[0], numbers[1])

    for n in numbers[2:]:
        res = np.gcd(res, n)

    numbers /= res


def explode_prices(matrix: DistanceMatrix, prices: np.ndarray) -> np.ndarray:
    ...
