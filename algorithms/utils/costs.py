import numpy as np


def get_inf(matrix: np.ndarray, mult: int = 30):
    """Длина ребра, такая, чтобы точно не попасть в тур."""
    # return get_length(np.arange(len(matrix)), matrix)
    # return matrix.sum()

    # noinspection PyArgumentList
    return matrix.max() * mult
