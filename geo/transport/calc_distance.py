from itertools import permutations
from typing import Optional, Tuple

import numpy as np
import pandas as pd
import tqdm
from geopy.distance import great_circle
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph._shortest_path import floyd_warshall

from geo.providers import osrm_module
from utils.logs import logger
from utils.types import Array

final_matrix_file = "data/full_matrix_27.npy.npz"


def great_circle_distance(a, b):
    """Расстояние по большой окружности."""
    return (great_circle(a, b).km / 5) * 3600


def build_full_matrix(
    walk_matrix: Array,
    station_df: pd.DataFrame,
    threshold=1200,  # Максимальное расстояние пешком в секундах
    transfer_cost=300,  # Ждать на остановке 5 минут
):
    """Собираем итоговую матрицу расстояний."""
    walk_matrix_reduced = walk_matrix.copy()
    walk_matrix_reduced[walk_matrix > threshold] = 0
    walk_matrix_reduced[walk_matrix_reduced != 0] += transfer_cost

    logger.info("Билдим итоговую матрицу алгоритмом floyd_warshall...")
    return build_graph(station_df, walk_matrix_reduced)


def build_stations_matrix(stations_df: pd.DataFrame, walk_matrix: Array):
    """Строим матрицу известных первичных расстояний между точками."""
    n = len(stations_df)
    map_dict = dict(zip(stations_df.index, list(range(n))))
    matrix = np.zeros((n, n), dtype=np.int32)

    for sid1, station_data in tqdm.tqdm(stations_df.iterrows()):
        for sid2, dist in station_data["links"].items():
            if sid2 not in map_dict:
                print(f"Station {sid2} have no coordinates, skipped")
                continue
            matrix[map_dict[sid1]][map_dict[sid2]] = dist
    # Правим получившуюся матрицу
    add_walk_matrix(matrix, walk_matrix)
    return matrix


def add_walk_matrix(stations_matrix: Array, walk_matrix: Array):
    """
    Объединяем пешеходную матрицу с матриццей станций
    TODO: тут косяк в логике. В stations_matrix уже учитывается ожидание.
        К каждой остановке прибавлено ожидание?
    """
    # matrix * walk_matrix != 0
    idx = (stations_matrix != 0) & (walk_matrix != 0)

    stations_matrix[idx] = np.minimum(stations_matrix, walk_matrix)[idx]  #
    stations_matrix[stations_matrix == 0] = walk_matrix[
        stations_matrix == 0
    ]  # заполняем пропуски


# @cache.memoize()
def build_graph(matrix: Array):
    """Построить граф перемещений по всем станциям."""

    logger.info(f"Рассчитываем floyd-warshall для объединенного графа")
    graph = csr_matrix(matrix)
    dist_matrix, predecessors = floyd_warshall(
        csgraph=graph, directed=True, return_predecessors=True
    )
    return dist_matrix


def transport_travel_time(
    src: int,
    dst: int,  # откуда до куда
    p_matrix: Array,  # время пешком между точками
    p2s_matrix: Array,  # время пешком от точек до остановок
    s2p_matrix: Array,  # время пешком от остановок до точек
    s_matrix: Array,  # время проезда между точками
    src_closest: Array,  # индексы ближайших к старту остановок
    dst_closest: Array,  # индексы ближайших к концу остановок
) -> Tuple[int, Optional[int], Optional[int]]:
    """Считаем время проезда из src в dst с учетом транспорта Возвращаем минимальное время и индексы
    остановок, если они есть, иначе None."""

    # считаем время на транспорте для каждой комбинации
    times = p2s_matrix[src, src_closest].reshape(-1, 1) + s2p_matrix[dst_closest, dst]
    times += s_matrix[np.ix_(src_closest, dst_closest)]

    # находим индексы лучших остановак в массивах closest
    min_idx = np.unravel_index(times.argmin(), times.shape)

    # считаем как быстрее: пешком или на транспорте и возвращаем
    if times[min_idx] < p_matrix[src, dst]:
        return times[min_idx], src_closest[min_idx[0]], dst_closest[min_idx[1]]
    else:
        return p_matrix[src, dst], None, None


def combined_matrix(
    p_matrix: Array,  # время пешком между точками
    p2s_matrix: Array,  # время пешком от точек до остановок
    s2p_matrix: Array,  # время пешком от остановок до точек
    s_matrix: Array,  # время проезда между точками
    candidates: int = 10,  # сколько ближайших остановок рассматривать
) -> Array:
    """Составляем матрицу времени перемещения от каждой точки до каждой с учетом тспользования транспорта."""

    # ближайшие станции к каждой точке в обоих направлениях
    src_closest = p2s_matrix.argpartition(kth=candidates, axis=1)[:candidates]
    dst_closest = s2p_matrix.T.argpartition(kth=candidates, axis=1)[:candidates]

    p = len(p_matrix)
    res_times = np.zeros((p, p), dtype="int32")

    logger.info("Считаем матрицу кратчайших проездов...")
    for src, dst in permutations(range(p), 2):
        time, src_s, dst_s = transport_travel_time(
            src=src,
            dst=dst,
            p_matrix=p_matrix,
            p2s_matrix=p2s_matrix,
            s2p_matrix=s2p_matrix,
            s_matrix=s_matrix,
            src_closest=src_closest[src],
            dst_closest=dst_closest[dst],
        )

        res_times[src, dst] = time

    return res_times


def get_travel_times(
    points: Array,
):
    stations = pd.read_pickle("./data/full_df_refactored.pkl")["coord"].values.tolist()
    stations = np.array(stations)

    p2s_matrix = osrm_module.get_osrm_matrix(points, stations)
    s2p_matrix = osrm_module.get_osrm_matrix(stations, points)
    p_matrix = osrm_module.get_osrm_matrix(points)
    s_matrix = np.load("./data/final_mat.npz")["walk_matrix"]

    return combined_matrix(p_matrix, p2s_matrix, s2p_matrix, s_matrix)
