from typing import Tuple, List

import numpy as np


def dumps_matrix(matrix: np.ndarray):
    """
    Сохраняем матрицу проблемы
    """
    assert len(matrix.shape) == 2 and matrix.shape[0] == matrix.shape[1]

    # матрица -> str разделенная пробелами
    matrix_s = "\n".join(
        " ".join(str(n) for n in row)
        for row in matrix
    )

    res = "\n".join([
        f"EDGE_WEIGHT_TYPE: EXPLICIT",
        f"EDGE_WEIGHT_FORMAT: FULL_MATRIX",
        f"EDGE_WEIGHT_SECTION",
        f"{matrix_s}",
    ])

    return res


def dumps_time_windows(time_windows: Tuple[Tuple[int, int], ...]):
    """
    Сохраняем временные окна проблемы
    """
    return '\n'.join(
        ['TIME_WINDOW_SECTION'] +
        [
            ' '.join([str(i), str(w[0]), str(w[1])])
            for i, w in enumerate(time_windows)
        ]
    )


def dump_demands(demands: List[int]):
    """
    Сохраняем спрос в каждой вершине
    """
    return '\n'.join(
        ['DEMAND_SECTION'] +
        [
            ' '.join([str(i), str(d)])
            for i, d in enumerate(demands)
        ]
    )
