from typing import Tuple

import pandas as pd
import regex


def parse_problem(
        coords_file: str,
        orders_file: str,
        stocks_file: str,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Загружем файлы в датафреймы
    """
    coords = pd.read_excel(coords_file)
    orders = pd.read_excel(orders_file)
    stocks = pd.read_excel(stocks_file)

    points = coords.join(orders)

    return points, stocks


def parse_time(points: pd.DataFrame):
    """
    Парсим время в датафреймах
    """
    # вытаскиваем время из строки
    time_regex = r'Доставка с ([0-9]{0,2}).* по ([0-9]{0,2}).*$'
    times = points['ИнтервалДоставки']
    t_from = times.map(lambda x: regex.search(time_regex, x).group(1))
    t_to = times.map(lambda x: regex.search(time_regex, x).group(2))

    # фиксим отсутствующие
    t_to[t_to == ''] = '24'
    t_from[t_from == ''] = '00'

    # фиксим типы данных
    t_to = t_to.astype(int)
    t_from = t_from.astype(int)

    # фиксим окна с неправиьным временем
    t_to[t_to <= t_from] = 24


def preprocess_data(
        points: pd. DataFrame,
        stocks: pd. DataFrame,
):
    stocks['lat'] = stocks['Широта']
    stocks['lng'] = stocks['Долгота']
