from typing import Tuple

import numba as nb

from utils.types import Array
import numpy as np


@nb.njit
def two_opt(
        tour: Array,
        matrices: Array,
        time_windows: Array,
        bad_windows: Array,
        weights: Array,
        delay: Array,
        offset: int,
        split: int
) -> Tuple[int, int, int, Array]:
    """
     Two Opt for Demo TSP
    :param tour: тур массивом
    :param matrices: матрица матриц
    :param time_windows: временные окна
    :param bad_windows: временные окна с опозданием
    :param weights: веса клиентские
    :param delay: задержка на клиенте
    :param offset: сдвиг для массив клиентских
    :param split: минуты
    :return: попадания, попадания с опозданием, стоимость, новый тур
    """
    hits, bad_hits, cost = get_demo_tsp_cost(tour, matrices, time_windows, bad_windows, offset, weights, delay, split)
    i, val = tour[0]
    val = tour[i - 1]
    info = tour[:i - 1]
    tour = tour[i - 1:]
    b_cost, b_hits, bb_hits, b_tour = cost, hits, bad_hits, tour
    bc_cost, bc_hits, bcb_hits = 1, 1, 1
    size = len(tour)

    while bc_cost > 0 or bc_hits > 0 or bcb_hits > 0:
        bc_cost, bc_hits, bcb_hits = 0, 0, 0

        for it1 in range(size):
            for it3 in range(it1 + 1, size):
                n_tour = rotate_value(swap(tour.copy(), it1, it3), val)
                n_hits, nb_hits, n_cost = get_demo_tsp_cost(
                    np.append(info, n_tour), matrices, time_windows, bad_windows, offset, weights, delay, split
                )
                if n_hits == -1:
                    continue
                c_cost, c_hits, cb_hits = cost - n_cost, n_hits - hits, nb_hits - bad_hits
                if bc_hits < c_hits or (bcb_hits < cb_hits and not bc_hits > c_hits) or \
                        (bc_cost < c_cost and not bc_hits > c_hits and not bcb_hits > cb_hits):
                    b_cost, b_hits, bb_hits, b_tour = n_cost, n_hits, nb_hits, n_tour
                    bc_hits, bcb_hits, bc_cost = c_hits, cb_hits, c_cost

        if bc_cost > 0 or bc_hits > 0 or bcb_hits > 0:
            cost, hits, bad_hits, tour = b_cost, b_hits, bb_hits, b_tour

    return hits, bad_hits, cost, np.append(info, tour)
