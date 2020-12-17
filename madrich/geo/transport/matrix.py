import os

import numpy as np
import pandas as pd

from madrich.config import settings
from madrich.geo.providers.osrm_module import get_osrm_matrix
from madrich.geo.transport import land, metro, suburban
from madrich.utils.logs import logger


def build_dataset_from_files():
    """Собираем общий объединенный датасет транспорта."""
    xml_url_out = ("https://metro.mobile.yandex.net/metro/get_file?file=scheme_1.xml&ver=")

    routes_file_pattern = "big/xls/data-101784-2020-04-08-s*.csv"
    routes_files = settings.DATA_DIR.glob(routes_file_pattern)

    xml_url_local = settings.DATA_DIR / "big/metro.xml"
    all_uids_file = settings.DATA_DIR / "big/all_uids.npy"
    all_pathes_file = settings.DATA_DIR / "big/all_pathes"
    stations_file = settings.DATA_DIR / "big/stations.json"
    bus_filename = settings.DATA_DIR / "big/raw_bus_data.pkl"
    merged_bus_filename = settings.DATA_DIR / "big/bus_data.pkl"

    xml_url = xml_url_local if os.path.exists(xml_url_local) else xml_url_out

    metro_df = metro.build_df(xml_url)
    suburban_df = suburban.build_df(all_uids_file, all_pathes_file)
    buses_df = land.build_df(stations_file, routes_files, bus_filename, merged_bus_filename)

    return metro_df.append([suburban_df, buses_df])


def build_walk_matrix(stations_df: pd.DataFrame):
    """Вычисляем расстояние между всеми станциями в датафрейме stations_df."""
    logger.info("Вычисляем матрицу расстояний остановок...")

    points = np.array(stations_df["coord"].values.tolist())[:, ::-1]
    return get_osrm_matrix(points, transport="foot")
