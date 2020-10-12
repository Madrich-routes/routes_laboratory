from typing import List, Set

import numpy as np

from utils.types import Array


def build_n_closest(matrix: Array, n: int):
    l = len(matrix)
    res = []

    for i in range(l):
        for j in np.argpartition(matrix[i], n)[:n]:
            res += [(i, j)]

    return res

# TODO: можем взять триангуляцию делоне и другие метрические штуки, так как у нас все же метрическая тема

# TODO: Не накладываем никаких ограничений на депо (ну или только если совсем далекие запретить)

# TODO: 12 кратчайших ребер из тех, что не нарушают
