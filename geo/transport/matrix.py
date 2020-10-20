import pandas as pd

from geo.providers.osrm_module import get_osrm_matrix
from geo.transport import land, metro, suburban
from utils.logs import logger
import glob, ujson


def build_dataset_from_files():
    """
    Собираем общий объединенный датасет транспорта
    """
    routes_file_pattern = f'../data/xls/data-101784-2020-04-08-s*.csv'
    xml_url = 'https://metro.mobile.yandex.net/metro/get_file?file=scheme_1.xml&ver='
    xml_url = '../data/metro.xml'
    all_uids_file = '../data/all_uids.npy'
    all_pathes_file = '../data/all_pathes'
    stations_file = '../data/stations.json'
    routes_files = glob.glob(routes_file_pattern)
    bus_filename = '../data/raw_bus_data.pkl'
    merged_bus_filename = '../data/bus_data.pkl'

    metro_df = metro.build_df(xml_url)
    suburban_df = suburban.build_df(all_uids_file, all_pathes_file)
    buses_df = land.build_df(stations_file, routes_files, bus_filename, merged_bus_filename)

    return metro_df.append([suburban_df, buses_df])


def build_walk_matrix(
        stations_df: pd.DataFrame
):
    """
    Вычисляем расстояние между всеми станциями в датафрейме stations_df
    """
    logger.info('Вычисляем матрицу расстояний остановок...')

    points = stations_df['coord'].values
    walk_matrix = get_osrm_matrix(points)

    return walk_matrix
