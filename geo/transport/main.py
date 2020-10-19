import argparse
import glob
import json
import logging
import os
from functools import partial
from multiprocessing import Pool

import numpy as np
import pandas as pd
import tqdm
from sklearn.metrics.pairwise import haversine_distances

from geo.transport.bus import BusWalker
from geo.transport.calc_distance import build_graph, calc_time
from geo.transport.metro import MetroWalker
from geo.transport.moscow_suburban import MOWalker


def join_df(routes_chunk_df, stations):
    bw = BusWalker(stations, routes_chunk_df)
    return bw.dataframe


def main():
    parser = argparse.ArgumentParser(description="Поиск времени в пути в душегубке")
    
    parser.add_argument(
        "--fr",
        default='55.750692,37.506783',
        help="55.783273,37.610669"
    )

    parser.add_argument(
        "--to",
        default='55.758270,37.551506',
        help="55.778724,37.646614"
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(lineno)d %(message)s"
    )
    all_uids_file = 'data/all_uids.npy'
    all_pathes_file = open("data/all_pathes", 'rb')
    xml_url = 'https://metro.mobile.yandex.net/metro/get_file?file=scheme_1.xml&ver='
    stations_file = open("data/stations.json", encoding='cp1251')
    routes_file_pattern = f'xls/data-101784-2020-04-08-s*.csv'
    matrix_file = "data/full_matrix_27.npy.npz"
    joined_df_file = "data/full_df_22.pkl"
    bus_file = 'data/bus_data.pkl'
    speed = 3600 / 5
    n_processes = 64
    threshold = 1200  # Максимальное расстояние пешком в секундах
    transfer_cost = 300  # Ждать на остановке 5 минут

    try:
        start = (float(args.fr.split(",")[0]), float(args.fr.split(",")[1]))
        finish = (float(args.to.split(",")[0]), float(args.to.split(",")[1]))
        logging.info(f'Вычисляю расстояние для {start} {finish}...')
    except:
        logging.error("Wrong coordinates {args.fr}.{args.to}")
        exit(-1)

    if not os.path.exists(joined_df_file):
        logging.info(f'Нет предрассчитанного файла {joined_df_file} - парсим данные')

        # Получить координаты, названия и прямые связи (соседние станции) для автобусов
        logging.info('Составляю словарь станций пригородных поездов и автобусов...')
        mo = MOWalker(all_uids_file=all_uids_file, all_pathes_file=all_pathes_file)

        # Получить координаты, названия и прямые связи (соседние станции) для метро
        logging.info('Составляю словарь станций метро...')
        metro = MetroWalker(xml_url)
        joined_df = mo.dataframe.append(metro.dataframe)

        # Все про наземный транспаорт
        logging.info('Составляю словарь наземного транспорта города Москва...')
        stations = json.load(stations_file)
        if not os.path.exists(bus_file):
            files = glob.glob(routes_file_pattern)
            logging.info(f"Получены {len(files)} файлов наземного транспорта типа {files[0]}")
            logging.info(f"Параллельная загрузка {len(files)} файлов ")
            process_pool = Pool(processes=len(files))
            # def load_fn(x):
            #     tmp_df = pd.read_csv(x, sep=';')
            #     return tmp_df
            dfs = process_pool.map(partial(pd.read_csv, sep=';'), files)
            routes_df = pd.concat(dfs)
            logging.info(f"Длина датасета {len(routes_df)}")
            routes_chunks = np.array_split(routes_df, n_processes)
            logging.info(f"Длина чанков {list(map(len, routes_chunks))}")

            process_pool = Pool(processes=n_processes)
            dfs = process_pool.map(partial(join_df, stations=stations), routes_chunks)
            bus_data = pd.concat(dfs)
            bus_data.to_pickle(bus_file)

        else:
            bus_data = pd.read_pickle(bus_file)

        if not os.path.exists(bus_file + "merged"):
            logging.info('Объединяю все маршруты')
            bus_stops = list(set(bus_data.index))
            merged_bus = pd.DataFrame(columns=bus_data.columns)
            for st in tqdm.tqdm(bus_stops):
                merged_bus.loc[st] = bus_data.loc[st].iloc[0]
                merged_bus.at[st, 'links'] = {k: v for d in bus_data.loc[st]['links'].values.tolist() for k, v in
                                              d.items()}

            merged_bus.to_pickle(bus_file + "merged")
        else:
            merged_bus = pd.read_pickle(bus_file + "merged")

        # Все остановки в одной базе
        logging.info('Сохраняю все маршруты')
        joined_df = joined_df.append(merged_bus)
        joined_df.to_pickle(joined_df_file)

    else:
        logging.info(f'Загружаем файл {joined_df_file}')
        joined_df = pd.read_pickle(joined_df_file)

    if not os.path.exists(matrix_file):
        # Все остановки в одной базе
        logging.info('Вычисляю попарные расстояния между всеми станциями...')
        walk_matrix = haversine_distances(np.array(list(joined_df['coord'].values))) * 6371 * speed
        walk_matrix_reduced = walk_matrix.copy()
        walk_matrix_reduced[walk_matrix > threshold] = 0
        walk_matrix_reduced[walk_matrix_reduced != 0] += transfer_cost
        logging.info('Строю граф для всех станций и пеших маршрутов...')
        matrix = build_graph(joined_df, walk_matrix_reduced)
        logging.info('Сохраняю матрицу...')
        np.savez_compressed(matrix_file, matrix=matrix)
    else:
        matrix = np.load(matrix_file)['matrix']

    bt = calc_time(start, finish, matrix, joined_df, transfer_cost)
    logging.info(f'Best time: {bt}')


if __name__ == "__main__":
    main()
