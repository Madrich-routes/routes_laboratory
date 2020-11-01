import collections
from datetime import datetime
from pathlib import Path

import pandas as pd
from more_itertools import flatten
from tqdm import tqdm

from customer_cases.krugoreys.data_processing.extract_data import load_data
from formats import sintef
from utils.logs import logger
from utils.serialization import load_np, read_pickle


def build_row(trip: int, time: int, vehicle: int):
    """
    Поменять соответствующую строчку в результируюзем excel
    """
    r = pretty_df.loc[trip]

    start_dt = datetime.fromtimestamp(time)
    end_dt = datetime.fromtimestamp(time + small_matrix[r.s_id][r.e_id])

    pretty_df[trip, 'start_time'] = start_dt
    pretty_df[trip, 'end_time'] = end_dt
    pretty_df[trip, 'osrm_dist'] = durations[trip] * speed
    pretty_df[trip, 'car'] = vehicles[vehicle].name


def rename_columns():
    global pretty_df
    pretty_df = pretty_df[
        [
            "start_time",
            "end_time",
            "addr1",
            "addr2",
            "coord1",
            "coord2",
            "osrm_dist",
            "line_dist",
            "car",
        ]
    ]

    pretty_df.columns = [
        "Время погрузки",
        "Время разгрузки",
        "Адрес погрузки",
        "Адрес разгрузки",
        "Координаты погрузки",
        "Координаты разгрузки",
        "Расстояние по дороге (км)",
        "Расстояние по прямой (км)",
        "Машина",
    ]


def get_original_tour():
    pretty_df.start_time = pd.to_datetime(pretty_df.start_time)
    res = []
    for v in vehicles:
        res += [pretty_df[pretty_df['car'] == v.name].sort_values(by='start_time', ascending=True).id.values]
    return res


def load_tours_sintef():
    # Решение
    logger.info(f'Всего трипов: {len(pretty_df)}')
    tours = sintef.parse_solution(data_dir / "mtsp_0.sintef")
    # tours = tsplib.parse_solution(data_dir / "mtsp_0.sol", points_num=len(pretty_df))

    for i in range(len(tours)):
        # вычитаем 1 потому что депо и индексация с 1
        tours[i] = [t - 1 for t in tours[i]]
        # if max(tours[i]) >= len(big_matrix):
        #     print('FUCK!')

    trips = list(flatten(tours))
    dup_trips = [item for item, count in collections.Counter(trips).items() if count > 1]

    assert len(dup_trips) == 0, str(dup_trips)
    print(f'Трипов в туре: {len(trips)}')

    return tours


def load_tours():
    # Решение
    logger.info(f'Всего трипов: {len(pretty_df)}')
    tours = sintef.parse_solution(data_dir / "cvrptw_first.sintef")
    # tours = tsplib.parse_solution(data_dir / "mtsp_0.sol", points_num=len(pretty_df))

    for i in range(len(tours)):
        # вычитаем 1 потому что депо и индексация с 1
        tours[i] = [t - 1 for t in tours[i]]
        # if max(tours[i]) >= len(big_matrix):
        #     print('FUCK!')

    trips = list(flatten(tours))
    dup_trips = [item for item, count in collections.Counter(trips).items() if count > 1]

    assert len(dup_trips) == 0, str(dup_trips)
    print(f'Трипов в туре: {len(trips)}')

    return tours


if __name__ == "__main__":

    speed = 18.87

    data_dir = Path("./data/")
    big_data_dir = Path("./big_data/")


    logger.info('Парсим матрицы и данные...')
    tasks = read_pickle(big_data_dir / "tasks.pkl.gz", compression="gzip")
    vehicles = read_pickle(big_data_dir / "vehicles.pkl.gz", compression="gzip")

    # Решение
    pretty_df = load_data(data_dir)  # обработанный excel
    tours = load_tours()
    orig_tours = get_original_tour()

    # tours = orig_tours

    # обе матрицы изначально содержат расстояния
    big_matrix = read_pickle(big_data_dir / "matrix_big.pkl.gz", compression='gzip').dist / speed
    big_matrix_dist = big_matrix * speed

    small_matrix = load_np(big_data_dir / "small_matrix.npz") / speed

    # Начало отсчета времен
    start_time = min(t.tw_start for t in tasks)
    durations = [small_matrix[r.s_id][r.e_id] / speed for r in pretty_df.itertuples()]

    res_dict = {}
    total_dist = 0
    total_errors = 0
    for car, tour in tqdm(enumerate(tours)):
        car_start_time = start_time
        for i in range(len(tour)):
            trip, next_trip = tour[i], tour[(i + 1) % len(tour)]

            res_dict[trip] = (car_start_time, car)
            car_start_time += max(big_matrix[trip, next_trip], 12 * 3600)
            car_start_time += durations[trip]

            total_dist += big_matrix_dist[trip, next_trip]
            total_errors += big_matrix_dist[trip, next_trip] > 80 * 1000

            print()

    print('Общее расстояние: ', total_dist / 1000, 'км')
    print('Общее количество ошибок: ', total_errors)

    pretty_df['start_time'] = pretty_df.id.map(
        lambda x: datetime.fromtimestamp(res_dict[x][0])
    )

    pretty_df['end_time'] = pretty_df.apply(
        lambda r: datetime.fromtimestamp(res_dict[r.id][0] + small_matrix[r.s_id][r.e_id]),
        axis=1,
    )

    pretty_df['osrm_dist'] = pretty_df.apply(lambda r: small_matrix[r.s_id][r.e_id] * speed, axis=1)
    pretty_df['car'] = pretty_df.id.map(lambda x: vehicles[res_dict[x][1]].name)

    pretty_df['osrm_dist'] /= 1000
    pretty_df['line_dist'] /= 1000

    rename_columns()  # делаем красиво
    pretty_df.to_excel("./pretty_res.xlsx")  # и сохраняем
