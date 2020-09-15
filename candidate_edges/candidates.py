from itertools import product

import numpy as np


def build_n_closest(matrix: np.ndarray, n: int):
    l = len(matrix)
    res = []

    for i in range(l):
        for j in np.argpartition(matrix[i], n)[:n]:
            res += [(i, j)]

    return res

# TODO: можем взять триангуляцию делоне и другие метрические штуки, так как у нас все же метрическая тема

# TODO: Не накладываем никаких ограничений на депо (ну или только если совсем далекие запретить)

# TODO: 12 кратчайших ребер из тех, что не нарушают
