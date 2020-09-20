import gzip
import math
import pickle
from datetime import timedelta

import mpu
import pandas as pd
from tqdm import tqdm
import numpy as np

from solving.models import Task, Vehicle, DistanceMatrix


def load_data():
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


df = load_data()
fix_data_errors(df)
small_matrix = pickle.load(gzip.open("../data/res_matrix.pkl.gz", "rb"))


def build_tasks():
    print('Создаем таски')
    tasks = []
    for r in tqdm(df.itertuples()):
        tasks += [Task(
            id=int(r.id) - 1,
            tw_start=str((r.start_time - timedelta(days=3)).strftime('%Y-%m-%dT%H:%M:%SZ')),
            tw_end=str((r.end_time + timedelta(days=3)).strftime('%Y-%m-%dT%H:%M:%SZ')),
            delay=int((r.end_time - r.start_time).seconds),
        )]
    with gzip.open('tasks.pkl.gz', 'wb') as f:
        pickle.dump(tasks, file=f, protocol=pickle.HIGHEST_PROTOCOL)


def build_matrix():
    print('Создаем матрицу')
    res_matrix = np.zeros((len(df), len(df)), dtype=np.int32)
    for r1 in tqdm(df.itertuples()):
        for r2 in df.itertuples():
            dist = small_matrix[r1.e_id][r2.s_id]

            if dist is None or not math.isfinite(dist):
                s_lat, s_lon = [float(c) for c in r1.coord2.split()]
                e_lat, e_lon = [float(c) for c in r2.coord1.split()]
                dist = mpu.haversine_distance((s_lat, s_lon), (e_lat, e_lon)) * 1000 * 1.23

            res_matrix[r1.id, r2.id] = int(dist)

    d_matr = DistanceMatrix(res_matrix, res_matrix / 18.87)

    with gzip.open('matrix.pkl.gz', 'wb') as f:
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
    build_tasks()
    build_cars()
    build_matrix()
