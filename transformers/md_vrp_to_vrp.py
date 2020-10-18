from typing import List

import numpy as np

from data_structures.tour.array_tour import get_inf
from utils.types import Array


def mdvrp_to_vrp(
        matrix: Array,
        depots: List[int],
        max_ins=50,
        max_outs=50,
):
    """
    Вместо каждого депо добавляется max_ins точек входа и max_ins точек выхода.
    Добавляется одно фейковое депо, связанное с каждым входом и выходом в правильном направлении.

    Расстояние между фейковым входом и выходом = inf
    """
    get_inf(matrix)
    n = len(matrix) + (len(max_ins) + len(max_outs)) * len(depots) + 1
    res = np.zeros((n, n))
