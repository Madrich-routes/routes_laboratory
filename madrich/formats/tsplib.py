import numpy as np
import tsplib95
from typing import List, Tuple


def dumps_matrix(matrix: np.ndarray):
    """Сохраняем матрицу проблемы."""
    assert len(matrix.shape) == 2 and matrix.shape[0] == matrix.shape[1]

    # матрица -> str разделенная пробелами
    matrix_s = "\n".join(
        " ".join(str(n) for n in row)
        for row in matrix
    )

    return "\n".join([
        r"EDGE_WEIGHT_TYPE: EXPLICIT",
        r"EDGE_WEIGHT_FORMAT: FULL_MATRIX",
        r"EDGE_WEIGHT_SECTION",
        f"{matrix_s}",
    ])


def dumps_time_windows(time_windows: List[Tuple[int, int]]):
    """Сохраняем временные окна проблемы. Индексация вершин начинается с 1.

    # TODO: написать warning для float
    """
    return '\n'.join(
        ['TIME_WINDOW_SECTION'] +
        [
            ' '.join([str(i + 1), str(int(w[0])), str(int(w[1]))])
            for i, w in enumerate(time_windows)
        ]
    )


def dump_demands(demands: List[int]):
    """Сохраняем спрос в каждой вершине.

    Индексация вершин начинается с 1
    """
    return '\n'.join(
        ['DEMAND_SECTION'] +
        [
            ' '.join([str(i + 1), str(d)])
            for i, d in enumerate(demands)
        ]
    )


def split_into_tours(nodes, size):
    nodes = np.array(nodes)
    bounds = list(np.where(nodes > size)[0])
    bounds.insert(0, 0)

    return [
        nodes[bounds[i]: bounds[i + 1]]
        for i in range(len(bounds) - 1)
    ] + nodes[bounds[-1]:]


def parse_solution(
        filename,
        points_num: int
):
    """Разобрать решение в формате MTSP."""
    tours = tsplib95.load(filename).tours[0]
    return split_into_tours(tours, points_num + 1)


if __name__ == '__main__':
    path = '/Users/dimitrius/projects/personal/VRP/customer_cases/krugoreys/data/mtsp_1.sol'
    sol = parse_solution(path, points_num=20745)
