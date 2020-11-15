from typing import List, Tuple

import numpy as np

from geo.transforms import delaunay_graph
from utils.types import Array


def build_n_closest(matrix: Array, n: int) -> List[Tuple[int, int]]:
    """Строми ребра-кандидаты из i по принципу "Берем n самых коротких ребер"."""
    l = len(matrix)
    res = []

    for i in range(l):
        for j in np.argpartition(matrix[i], n)[:n]:
            res += [(i, j)]

    return res


def pure_delaunay(points: Array, n: int):
    """Берем только те ребра, которые напрямую входят в триангуляцию делоне."""
    return delaunay_graph(points)

# TODO: взять триангуляцию делоне как у хельсгауна

# TODO: Не накладываем никаких ограничений на депо (ну или только если совсем далекие запретить)

# TODO: 12 кратчайших ребер из тех, что не нарушают ограничения

# TODO: Popmusic подход
