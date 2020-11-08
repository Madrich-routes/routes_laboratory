import json
import os
from functools import partial
from multiprocessing import Pool
from typing import Dict, List

import numpy as np
import pandas as pd
from more_itertools import windowed
from tqdm import tqdm

# from geo.transport import bus
from utils.logs import logger


def id_to_idx(id) -> str:
    """Добавляем bus к id."""
    return f'bus_{id}'


def build_df(
    stations_file: str,
    routes_files: List[str],
    bus_filename: str,
    merged_bus_filename: str,
):
    """Собираем датафрейм с информацией про автобусы.

    * stations_file - скачать с сайта
    * routes_files - скачать с сайта и разбить на файлы до 1миллиона строк
    """
    # парсим все остановки наземного транспорта в словарик с координатами и именами
    # подгружаем все файлики в один большой датафрейм
    if os.path.exists(merged_bus_filename):
        logger.info('Загружаем датафрейм с соседними станциями наземного транспорта...')
        merged_bus_df = pd.read_pickle(merged_bus_filename)
    else:
        transport_dict = load_transport_dict(stations_file)
        stations = build_station_data(transport_dict)
        if os.path.exists(bus_filename):
            bus_df = pd.read_pickle(bus_filename)
        else:
            logger.info('Считаем датафрейм с соседними станциями наземного транспорта')
            bus_df = load_bus_file(routes_files, bus_filename, stations, n_processes=os.cpu_count())
        merged_bus_df = merge_bus_data(bus_df, merged_bus_filename)
    return merged_bus_df


def load_transport_dict(stations_file: str):
    """Загружаем словарь наземного транспорта."""
    logger.info('Загружаем словарь наземного траспорта города Москва...')
    return json.load(open(stations_file, 'r', encoding='cp1251'))


def build_station_data(stations: List[Dict]):
    """Строим данные автобусных станций."""
    return {
        id_to_idx(station['ID']): {
            'coord': station['geoData']['coordinates'][::-1],
            'name': station['Name'],
            'links': {},
        }
        for station in stations
    }


def read_csv(f):
    return pd.read_csv(f, sep=';')


def load_bus_file(
    filenames: List[str],
    bus_filename: str,
    stations: Dict,
    n_processes: int = os.cpu_count(),
):
    """Загружем информацию об автобусах в датафрейм Сохраняем этот dataframe в bus_filename."""
    logger.info(f'Загружем информацию об автобусах ({len(filenames)}) потоков...')
    process_pool = Pool(processes=len(filenames))
    dfs = process_pool.map(read_csv, filenames)
    process_pool.close()

    logger.info(f'Объединяем датафреймы...')
    routes_df = pd.concat(dfs)

    logger.info(f"Джойним станции. Строчек: {len(routes_df)}, процессов: {n_processes}")
    routes_chunks = np.array_split(routes_df, n_processes)
    process_pool = Pool(processes=n_processes)
    # join_df(routes_chunks[0], stations=stations)
    dfs = process_pool.map(partial(join_df, stations=stations), routes_chunks)
    bus_data = pd.concat(dfs)
    process_pool.close()

    logger.info(f"Сохраняем инфу про автобусам")
    bus_data.to_pickle(bus_filename)
    return bus_data


def merge_bus_data(
    bus_data: pd.DataFrame,
    merged_bus_filename: str,
):
    """Мержим данные автобусов.

    # TODO: ??
    """
    logger.info('Объединяем все маршруты автобусов...')
    bus_stops = bus_data.index.unique().tolist()
    merged_bus_data = pd.DataFrame(columns=bus_data.columns)

    for st in tqdm(bus_stops):
        merged_bus_data.loc[st] = bus_data.loc[st].iloc[0]
        merged_bus_data.at[st, 'links'] = {
            k: v for d in bus_data.loc[st]['links'].values.tolist() for k, v in d.items()
        }

    merged_bus_data.to_pickle(merged_bus_filename)
    return merged_bus_data


# Основное отделение - сбор данных в параллель
def join_df(routes_chunk_df, stations):
    """
    TODO: ?
    """
    return build_dataframe(stations, routes_chunk_df)


def build_dataframe(
    data: Dict,
    routes_df: pd.DataFrame,
):
    """Собираем датафрейм с информацией про автобусы."""
    add_travel_times(data, routes_df)
    dataframe = pd.DataFrame.from_dict(data, orient='index')
    return dataframe.dropna()


def add_travel_times(
    data: Dict,
    routes_df: pd.DataFrame,
):
    """
    Добавляем данные о времени перемещения
    TODO: переписать по человечески
    """
    all_routes = sorted(routes_df['trip_id'].unique())  # routes_df['trip_id'].unique().sort_values().values
    for route_id in tqdm(all_routes):
        route = routes_df[routes_df['trip_id'] == route_id]
        stops = sorted(route['stop_sequence'].unique())
        # route['stop_sequence'].unique().sort_values().values

        for fr_num, to_num in windowed(stops, n=2):
            if to_num not in route['stop_sequence'].values or fr_num not in route['stop_sequence'].values:
                # Дробление на подфреймы приводит трассы + края не в маршруте
                logger.info(f'{to_num} or {fr_num} not in route {route_id}')
                continue
            fr = route[route['stop_sequence'] == fr_num]
            to = route[route['stop_sequence'] == to_num]

            start_id = id_to_idx(fr['stop_id'].values[0])
            stop_id = id_to_idx(to['stop_id'].values[0])

            travel_time = trip_time(fr['departure_time'].values[0], to['arrival_time'].values[0])

            if start_id in data and stop_id in data:
                data[start_id]['links'][stop_id] = travel_time


def to_secs(str_time: str) -> int:
    """Парсим время и превращаем в секунды."""
    clock = str_time.split(':')
    return int(clock[0]) * 3600 + int(clock[1]) * 60 + int(clock[2])


def trip_time(from_str: str, to_str: str) -> int:
    """Время поездки в секундах."""
    diff = to_secs(to_str) - to_secs(from_str)
    return abs(diff)
