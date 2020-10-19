import pandas as pd

from geo.providers.osrm_module import get_osrm_matrix
from geo.transport import land, metro, suburban
from utils.logs import logger


def build_dataset():
    """
    Собираем общий объединенный датасет транспорта
    """
    metro_df = metro.build_df()
    suburban_df = suburban.build_df()
    buses_df = land.build_df()

    return metro_df.append([suburban_df, buses_df])


def build_matrix(
        stations_df: pd.DataFrame
):
    """
    Вычисляем расстояние между всеми станциями в датафрейме stations_df
    """
    logger.info('Вычисляем матрицу расстояний остановок...')

    points = stations_df['coord'].values
    walk_matrix = get_osrm_matrix(points)

    return walk_matrix
