import numpy as np
import pandas as pd
import tqdm
from geopy.distance import great_circle
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph._shortest_path import floyd_warshall

from utils.logs import logger
from utils.types import Array

final_matrix_file = "data/full_matrix_27.npy.npz"


def great_circle_distance(a, b):
    """
    Расстояние по большой окружности
    """
    return (great_circle(a, b).km / 5) * 3600


def build_full_matrix(
        walk_matrix: Array,
        station_df: pd.DataFrame,
        threshold=1200,  # Максимальное расстояние пешком в секундах
        transfer_cost=300,  # Ждать на остановке 5 минут
):
    """
    Собираем итоговую матрицу расстояний
    """
    walk_matrix_reduced = walk_matrix.copy()
    walk_matrix_reduced[walk_matrix > threshold] = 0
    walk_matrix_reduced[walk_matrix_reduced != 0] += transfer_cost

    logger.info('Билдим итоговую матрицу алгоритмом floyd_warshall...')
    matrix = build_graph(station_df, walk_matrix_reduced)
    return matrix


def build_stations_matrix(stations_df: pd.DataFrame):
    """
    Строим матрицу известных первичных расстояний между точками
    """
    n = len(stations_df)
    map_dict = dict(zip(stations_df.index, list(range(n))))
    matrix = np.zeros((n, n), dtype=np.int32)

    for sid1, station_data in tqdm.tqdm(stations_df.iterrows()):
        for sid2, dist in station_data['links'].items():
            if sid2 not in map_dict:
                print(f"Station {sid2} have no coordinates, skipped")
                continue
            matrix[map_dict[sid1]][map_dict[sid2]] = dist

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
    stations_matrix[stations_matrix == 0] = walk_matrix[stations_matrix == 0]  # заполняем пропуски


def build_graph(
        stations_df: pd.DataFrame,
        walk_matrix: Array,
):
    """
    Построить граф перемещений по всем станциям
    """
    matrix = build_stations_matrix(stations_df)
    add_walk_matrix(matrix, walk_matrix)

    logger.info(f"Рассчитываем floyd-warshall для объединенного графа")
    graph = csr_matrix(matrix)
    dist_matrix, predecessors = floyd_warshall(csgraph=graph, directed=True, return_predecessors=True)

    logger.info('Сохраняю матрицу...')
    np.savez_compressed(final_matrix_file, matrix=matrix, predecessors=predecessors)

    return dist_matrix


def closest_stations(
        p2s_matrix: Array,  # время пешком от точек до остановок
        k: int = 10,
):
    indices = p2s_matrix.argpartition(kth=k, axis=1)


def combined_matrix(
        p_matrix: Array,  # время пешком между точками
        p2s_matrix: Array,  # время пешком от точек до остановок
        s2p_matrix: Array,  # время пешком от остановок до точек
        s_matrix: Array,  # время проезда между точками
        s_walk_matrix: Array,  # время проезда между точками
        candidates: int = 10,  # сколько ближайших остановок рассматривать
):
    """
    Составляем матрицу времени перемещения с учетом транспортных матриц
    """
    p2s_matrix.argpartition(axis=1)
    p2s_matrix.argsort(axis=1)

    np = len(p_matrix)
    ns = len(s_matrix)

    for p_from in range(np):
        ...



def calc_time(start, finish, matrix, dataframe, transfer_cost=0):
    """
    Посчитать время в секундах между А и Б для матрицы перемещений, используя координаты и названия станций из датасета
    """
    station_map = dict(zip(dataframe.index, range(len(dataframe))))
    by_walk = great_circle_distance(start, finish)

    # print(f"Time by walk: {by_walk:.2f}sec")
    dataframe['from_start'] = list(map(lambda x: great_circle_distance(start, x), dataframe['coord']))
    dataframe['from_finish'] = list(map(lambda x: great_circle_distance(x, finish), dataframe['coord']))

    best_time = by_walk
    best_route = None

    for fr in dataframe.sort_values(by='from_start')[:10].index:
        print(f'Closest: fr {fr}')
        for to in dataframe.sort_values(by='from_finish')[:10].index:
            print(f'Closest: to {to}')
            budget = transfer_cost + matrix[station_map[fr], station_map[to]] + dataframe['from_start'][fr] + \
                     dataframe['from_finish'][to]
            if budget <= best_time:
                best_time = budget
                best_route = [fr, to]
            best_time = min(best_time, budget)

            ### Printing
            print(f"Time for route {fr}->{to}:\t \
                    walk: {dataframe['from_start'][fr]:.2f} + wait: {transfer_cost:.2f} + transport:{matrix[station_map[fr]][station_map[to]]:.2f} + \
                    walk: {dataframe['from_finish'][to]:.2f} = {budget:.2f}sec")

    if best_route is not None:
        print(
            f"Best time: {best_time:.2f}sec, Best route: {dataframe.loc[best_route[0], 'name']}->{dataframe.loc[best_route[1], 'name']}")
        print(f"Best time: {best_time:.2f}sec, Best route code: {best_route[0]}->{best_route[1]}")
    else:
        print(f"Best time: {best_time:.2f}sec, walking")

    return best_time
