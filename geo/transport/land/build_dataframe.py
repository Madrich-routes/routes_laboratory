import glob
import os
from functools import partial
from multiprocessing import Pool
from typing import Tuple, List, Dict

import numpy as np
import pandas as pd
import ujson
from tqdm import tqdm

from geo.transport import bus
from geo.transport.calc_distance import build_graph
from utils.logs import logger
from utils.types import Array

routes_file_pattern = f'xls/data-101784-2020-04-08-s*.csv'


def join_df(routes_chunk_df, stations):
    """
    TODO: ?
    """
    return bus.build_dataframe(stations, routes_chunk_df)


def load_transport_dict(stations_file: str):
    """
    Загружаем словарь наземного транспорта
    """
    logger.info('Загружаем словарь наземного траспорта города Москва...')
    return ujson.load(stations_file)


def build_land_transport(routes_glob: str):
    """
    Получаем все файлы с маршрутами
    """
    return glob.glob(routes_glob)
    # logger.info(f"Получены {len(files)} файлов наземного транспорта типа {files[0]}")


def load_bus_file(
        filenames: List[str],
        bus_filename: str,
        stations: Dict,
        n_processes: int = os.cpu_count(),
):
    """
    Загружем информацию об автобусах в датафрейм
    Сохраняем этот dataframe в bus_filename
    """
    logger.log(f'Загружем информацию об автобусах ({len(filenames)}) потоков...')
    process_pool = Pool(processes=len(filenames))
    dfs = process_pool.map(partial(pd.read_csv, sep=';'), filenames)

    logger.log(f'Объединяем датафреймы...')
    routes_df = pd.concat(dfs)

    logger.log(f"Джойним станции. Строчек: {len(routes_df)}, процессов: {n_processes}")
    routes_chunks = np.array_split(routes_df, n_processes)
    process_pool = Pool(processes=n_processes)
    dfs = process_pool.map(partial(join_df, stations=stations), routes_chunks)
    bus_data = pd.concat(dfs)

    logger.debug(f"Сохраняем инфу про автобусам")
    bus_data.to_pickle(bus_filename)


def merge_bus_data(
        bus_data: pd.DataFrame,
        merged_bus_filename: str,
):
    """
    Мержим данные автобусов
    # TODO: ??
    """
    logger.info('Объединяем все маршруты автобусов...')
    bus_stops = bus_data.index.unique().tolist()
    merged_bus = pd.DataFrame(columns=bus_data.columns)

    for st in tqdm(bus_stops):
        merged_bus.loc[st] = bus_data.loc[st].iloc[0]
        merged_bus.at[st, 'links'] = {
            k: v
            for d in bus_data.loc[st]['links'].values.tolist()
            for k, v in d.items()
        }

    merged_bus.to_pickle(merged_bus_filename)
