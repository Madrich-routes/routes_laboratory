import gzip
import pickle
from datetime import timedelta

import numpy as np
import pandas as pd
from tqdm import tqdm

from customer_cases.krugoreys.solving.models import Vehicle, DistanceMatrix, Task
from geo.martices.osrm import fix_matrix
from utils.serialization import read_pickle


def load_data():
    print('Читаем excel...')
    df = pd.read_excel("../data/pretty_result.xlsx")  # noqa
    df.columns = ['id', "start_time", "end_time", "addr1", "addr2", "coord1", "coord2",
                  's_id', 'e_id', "line_dist", "osrm_dist", "car"]
    return df


def get_dist_coeff(df: pd.DataFrame):
    """
    Коэффициент расстояния = 1.23
    Скорость 18.87 м/c
    """
    good_data = df[~df['osrm_dist'].isna()]
    osrm = good_data['osrm_dist'].sum()
    line = good_data['line_dist'].sum()

    time = (good_data.end_time - good_data.start_time).dt.seconds.sum()

    return osrm / line, osrm / time


def fix_data_errors(df: pd.DataFrame):
    """
    Чиним косяки и преобразуем типы
    """
    df['osrm_dist'] = df.osrm_dist.fillna(df.line_dist * 1.23)
    df.start_time = pd.to_datetime(df.start_time)
    df.end_time = pd.to_datetime(df.end_time)


def build_tasks():
    print('Создаем таски')
    tasks = []
    for r in tqdm(df.itertuples()):
        tasks += [Task(
            id=int(r.id) - 1,
            tw_start=(r.start_time - timedelta(days=3)).timestamp(),
            tw_end=(r.end_time + timedelta(days=3)).timestamp(),
            delay=int((r.end_time - r.start_time).seconds),
        )]
    with gzip.open('tasks.pkl.gz', 'wb') as f:
        pickle.dump(tasks, file=f, protocol=pickle.HIGHEST_PROTOCOL)


def build_matrix():
    print('Создаем матрицу...')

    e_idx = df.e_id.values
    s_idx = df.s_id.values
    res_matrix = small_matrix[e_idx][:, s_idx].astype(np.int32)

    d_matr = DistanceMatrix(res_matrix, speed=18.87)

    print('Записываем матрицу на диск...')
    with gzip.open('matrix.pkl.gz', 'wb', compresslevel=6) as f:
        pickle.dump(d_matr, file=f, protocol=pickle.HIGHEST_PROTOCOL)


def build_cars():
    print('Создаем машины')
    vehicles = []
    vehicle_ids = df['car'].dropna().unique()
    for vid in tqdm(vehicle_ids):
        try:
            trips = df[df['car'] == vid]
            first, last = trips.iloc[0], trips.iloc[-1]

            res = Vehicle(
                start_place=int(first.e_id),
                end_place=int(last.s_id),
                start_time=str(first.end_time.strftime('%Y-%m-%dT%H:%M:%SZ')),
                end_time=str(last.start_time.strftime('%Y-%m-%dT%H:%M:%SZ')),
                costs=dict(
                    fixed=10,
                    time=10,
                    distance=10
                ),
                value=10000000,
            )
            vehicles += [res]
        except KeyError as e:
            print(e)
    with gzip.open('vehicles.pkl.gz', 'wb') as f:
        pickle.dump(vehicles, file=f, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__":
    df = load_data()
    fix_data_errors(df)
    small_matrix = read_pickle("../data/res_matrix.pkl.gz", compression="gzip")
    coords = pd.read_csv("../data/coordinates.csv", sep=';')[["0", "1"]].values
    small_matrix = fix_matrix(matrix=small_matrix, coords=coords, coeff=1.23)

    build_tasks()
    build_cars()
    build_matrix()
