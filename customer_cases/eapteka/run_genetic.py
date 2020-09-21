import math
from collections import defaultdict
from typing import Tuple, Dict, List

import pandas as pd

from customer_cases.eapteka.genetic_solver.models import Courier, Depot, Task
from customer_cases.eapteka.genetic_solver.runner import multi_runner


def make_windows_orders(date: str, interval: str) -> List[Tuple[str, str]]:
    start, end = f'{date}T00:00:00Z', f'{date}T23:59:00Z'
    tokens = interval.split(' ')
    size = len(tokens)
    for i, token in enumerate(tokens):
        if token == 'с' and i != size - 1:
            if tokens[i + 1]:
                start = f'{date}T{tokens[i + 1]}:00Z'
        if token == 'по' and i != size - 1:
            if tokens[i + 1]:
                end = f'{date}T{tokens[i + 1]}:00Z'
    return [(start, end)]


def make_windows(date: str, interval: str) -> List[Tuple[str, str]]:
    if interval == 'круглосуточно':
        return [(f'{date}T00:00:00Z', f'{date}T23:59:59Z')]
    start, end = interval.split('-')
    start = f'0{int(start)}:00' if int(start) < 10 else f'{start}:00'
    if int(end) < 10:
        end = f'0{int(end)}:00'
    else:
        end = f'{end}:00' if int(end) != 24 else f'23:59'
    return [(f'{date}T{start}:00Z', f'{date}T{end}:00Z')]


def parse_data(couriers_file: str, clear_orders_file: str, orders_file: str, storages_file: str
               ) -> Tuple[Dict[str, List[Task]], Dict[str, Depot], List[Courier], Dict[Tuple[float, float], int]]:
    courier_typing = {'Водитель': 'driver', 'Курьер': 'pedestrian'}
    mapping, index = {}, 0

    def add_point(idx: int, lat: float, lon: float) -> Tuple[int, int]:
        point = (lat, lon)
        if point not in mapping:
            mapping[point] = idx
            idx += 1
        return mapping[point], idx

    orders, errors = defaultdict(list), 0
    orders_lx = pd.read_excel(orders_file)
    orders_coords_xl = pd.read_excel(clear_orders_file)
    orders_all_xl = pd.concat([orders_lx, orders_coords_xl.reindex(orders_lx.index)], axis=1)
    date = orders_all_xl.iloc[0]['ДатаДоставки']
    date = f'{date[6:10]}-{date[3:5]}-{date[0:2]}'
    for i, row in orders_all_xl.iterrows():
        try:
            __check_point(float(row['Широта']), float(row['Долгота']))
            point_index, index = add_point(index, float(row['Широта']), float(row['Долгота']))
            time_windows = make_windows_orders(date, row['ИнтервалДоставки'])
            value = [
                int(float(row['ВесЗаказа'] if not math.isnan(row['ВесЗаказа']) else 0.099) * 1e3),
                int(float(row['ОбъемЗаказа'] if not math.isnan(row['ОбъемЗаказа']) else 0.099) * 1e3)
            ]
            priority = 2 if math.isnan(row['Приоритет']) else int(row['Приоритет'])
            orders[row['Склад']].append(Task(point_index, time_windows, 0., value, priority))
        except Exception as exc:
            errors += 1
            if not math.isnan(row['Приоритет']):
                print(exc)
                print(i, row['Долгота'], row['Широта'])
    print('Errors ignored:', errors)

    couriers = []
    courier_xl = pd.read_excel(couriers_file)
    for i, row in courier_xl.iterrows():
        priority = int(row['Приоритет'] if not math.isnan(row['Приоритет']) else 2)
        cost = int(row['Стоимость 1 заказа']) if priority == 1 else 1000 + int(row['Стоимость 1 заказа'])
        courier = Courier(type_id=f'courier_{i}', profile=courier_typing[row['Должность']],
                          name=f'{row["Сотрудник"]}_id_{i}', value=[int(1e8), int(1e8)],
                          costs={"time": 0., "distance": 0., "fixed": cost},
                          time_windows=make_windows(date, row['Интервал работы']),
                          priority=priority, start=-1, end=-1)
        couriers.append(courier)

    depots_xl = pd.read_excel(storages_file)
    depots = {}
    for i, row in depots_xl.iterrows():
        depot_loc, index = add_point(index, float(row['Долгота']), float(row['Широта']), )
        depot = Depot(row['Наименование'], depot_loc, 0., 0., make_windows(date, row['График работы'])[0])
        depots[row['Наименование']] = depot

    print('Couriers:', len(couriers))
    print('Orders:', sum([len(tasks) for _, tasks in orders.items()]), 'to', len(orders))
    print('Depots:', len(depots))
    print('Orders to depot:', [len(tasks) for _, tasks in orders.items()])

    return orders, depots, couriers, mapping


def __check_point(lat, lon):
    assert 54.288066 < lat < 57.172201, f'bad point {lat}'
    assert 34.619289 < lon < 39.724750, f'bad point {lon}'


def run_solver(couriers_file: str, clear_orders_file: str, orders_file: str, storages_file: str):
    print('Started')
    print('Converting...')
    orders, depots, couriers, mapping = parse_data(couriers_file, clear_orders_file, orders_file, storages_file)

    print('Done, Starting solver...', '\n')
    answer = multi_runner(orders, depots, couriers, mapping)
    print('Ended')
    print(answer)
    return answer


run_solver('./data/Курьеры_13.xlsx', './data/eapteka_result.xlsx', './data/Заказы_13.xlsx', './data/Склады.xlsx')
