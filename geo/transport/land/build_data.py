from typing import Dict

import pandas as pd
from more_itertools import windowed
from tqdm import tqdm


def id_to_idx(id) -> str:
    """
    Добавляем bus к id
    """
    return f'bus_{id}'


def to_secs(str_time: str) -> int:
    """
    Парсим время и превращаем в секунды
    """
    clock = str_time.split(':')
    sec = int(clock[0]) * 3600 + int(clock[1]) * 60 + int(clock[2])
    return sec


def trip_time(from_str: str, to_str: str) -> int:
    """
    Время поездки в секундах
    """
    diff = to_secs(to_str) - to_secs(from_str)
    return abs(diff)


def build_station_data(stations: Dict):
    """
    Строим данные автобусных станций
    """
    return {
        id_to_idx(station['ID']): {
            'coord': station['geoData']['coordinates'][::-1],
            'name': station['Name'],
            'links': {},
        }
        for station in stations
    }


def add_travel_times(
        data: Dict,
        routes_df: pd.DataFrame,
):
    """
    Добавляем данные о времени перемещения
    TODO: переписать по человечески
    """
    all_routes = routes_df['trip_id'].unique().sort_values().values
    for route_id in tqdm(all_routes):
        route = routes_df[routes_df['trip_id'] == route_id]
        stops = route['stop_sequence'].unique().sort_values().values

        for fr_num, to_num in windowed(stops, n=2):
            fr = route[route['stop_sequence'] == fr_num]
            to = route[route['stop_sequence'] == to_num]

            start_id = id_to_idx(fr['stop_id'].values[0])
            stop_id = id_to_idx(to['stop_id'].values[0])

            travel_time = trip_time(fr['departure_time'].values[0], to['arrival_time'].values[0])

            if start_id in data and stop_id in data:
                data[start_id]['links'][stop_id] = travel_time


def build_df(
        stations: Dict,
        routes_df: pd.DataFrame,
):
    """
    Собираем датафрейм с информацией про автобусы
    """
    data = build_station_data(stations)
    add_travel_times(data, routes_df)
    dataframe = pd.DataFrame.from_dict(data, orient='index')
    return dataframe.dropna()
