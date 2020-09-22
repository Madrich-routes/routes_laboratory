from datetime import datetime
from pathlib import Path

from tqdm import tqdm

from customer_cases.krugoreys.data_processing.extract_data import load_data
from formats import sintef
from utils.logs import logger
from utils.serialization import read_pickle, load_np


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


def load_tours():
    # Решение
    tours = sintef.parse_solution(data_dir / "sintef_sol.lkh")
    for i in range(len(tours)):
        # вычитаем 1 потому что было депо
        tours[i] = [t - 1 for t in tours[i]]

    return tours


if __name__ == "__main__":

    speed = 18.87

    data_dir = Path("./data/")
    big_data_dir = Path("./big_data/")

    # Решение
    tours = load_tours()
    pretty_df = load_data(data_dir)  # обработанный excel

    logger.info('Парсим матрицы и данные...')
    tasks = read_pickle(big_data_dir / "tasks.pkl.gz", compression="gzip")
    vehicles = read_pickle(big_data_dir / "vehicles.pkl.gz", compression="gzip")

    # обе матрицы изначально содержат расстояния
    big_matrix = read_pickle(big_data_dir / "matrix_big.pkl.gz", compression='gzip').dist / speed
    small_matrix = load_np(big_data_dir / "small_matrix.npz") / speed

    # Начало отсчета времен
    start_time = min(t.tw_start for t in tasks)
    durations = [small_matrix[r.s_id][r.e_id] / speed for r in pretty_df.itertuples()]

    res_dict = {}
    for car, tour in tqdm(enumerate(tours)):
        car_start_time = start_time
        for i in range(len(tour)):
            trip, next_trip = tour[i], tour[(i + 1) % len(tour)]

            res_dict[trip] = (car_start_time, car)
            car_start_time += (big_matrix[trip, next_trip])
            car_start_time += durations[trip]

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
