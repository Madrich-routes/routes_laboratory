import logging
import math
from collections import defaultdict
from typing import Tuple, List, Dict

import numpy as np
import pandas as pd
import ujson
from transliterate import translit

from customer_cases.eapteka.genetic_solver.models import Task, Courier, Depot
from customer_cases.eapteka.genetic_solver.utils import check_point, make_windows_orders, make_windows
from geo.providers import osrm_module
from geo.providers.osrm_module import _turn_over
from geo.transport.calc_distance import get_travel_times
from solvers.madrich.utils import to_array
from utils.types import Array

Point = Tuple[float, float]


def __add_point(mapping: dict, idx: int, lt: float, ln: float) -> Tuple[int, int]:
    """ Add point in mapping dict """
    point = (lt, ln)
    if point not in mapping:
        mapping[point] = idx
        idx += 1
    return mapping[point], idx


def parse_orders(
        aver: float,
        index: int,
        mapping: dict,
        minutes: int,
        border: str = 'nemkad'
) -> Tuple[int, str, Dict[str, List[Task]]]:
    """
    Парсим заказы
    """
    logging.info('Парсим заказы...')
    orders, errors = defaultdict(list), 0
    orders_inf = pd.read_excel('./data/Заказы_13.xlsx')
    orders_loc = pd.read_excel('./data/update_3.xlsx')

    date = orders_inf.iloc[0]['ДатаДоставки']
    date = f'{date[6:10]}-{date[3:5]}-{date[0:2]}'

    center = (
        sum(orders_loc.lat) / len(orders_loc.index),
        sum(orders_loc.lng) / len(orders_loc.index),
    )  # нахождение центра масс точек

    # задаем ограничительный радиус для точек в градусах
    radius = 0.25 if border == 'mkad' else 0.5

    for i, row in orders_inf.iterrows():
        try:
            lat, lng = orders_loc['lat'][i], orders_loc['lng'][i]
            check_point(lat, lng, center, radius)
            point_index, index = __add_point(mapping, index, lat, lng)
            time_windows = make_windows_orders(date, row['ИнтервалДоставки'])
            if math.isnan(row['ВесЗаказа']) and not math.isnan(row['ОбъемЗаказа']):
                value = [int(aver * row['ОбъемЗаказа'] * 100), int(row['ОбъемЗаказа'] * 100)]
            elif not math.isnan(row['ВесЗаказа']) and math.isnan(row['ОбъемЗаказа']):
                value = [int(row['ВесЗаказа'] * 100), int(1 / aver * row['ВесЗаказа'] * 100)]
            elif math.isnan(row['ВесЗаказа']) and math.isnan(row['ОбъемЗаказа']):
                value = [int(0.5 * 100), int(2 * 100)]
            else:
                value = [int(row['ВесЗаказа'] * 100), int(row['ОбъемЗаказа'] * 100)]
            priority = 2 if math.isnan(row['Приоритет']) else int(row['Приоритет'])
            storage = row['Склад'].replace(' ', '').replace('/', '-').replace('Мск,', '')
            orders[storage].append(Task(point_index, time_windows, minutes * 60, value, priority))

        except Exception as exc:
            errors += 1
            if not math.isnan(row['Приоритет']):
                lat, lng = orders_loc['lat'][i], orders_loc['lng'][i]
                # print(i, lat, lng, orders_loc['place'][i])
                # print(exc)

    # logging.info(f'Ignored: {errors}\n')
    return index, date, orders


def parse_couriers(date: str, courier_typing: dict, t_w, t_c, d_w, d_c) -> List[Courier]:
    """ Parse couriers data
    """
    logging.info('Parsing couriers...')
    couriers = {}
    couriers_data = pd.read_excel('./data/Курьеры_13.xlsx')

    for i, row in couriers_data.iterrows():
        name = translit(f'{row["Сотрудник"]}', 'ru', reversed=True)
        if name not in couriers:
            priority = int(row['Приоритет'] if not math.isnan(row['Приоритет']) else 2)
            cost = int(row['Стоимость 1 заказа']) if priority == 1 else int(row['Стоимость 1 заказа'])
            profile = courier_typing[row['Должность']]
            value = [d_w * 100, d_c * 100] if profile == 'driving' else [t_w * 100, t_c * 100]
            courier = Courier(
                type_id=f'courier_{i}',
                profile=profile,
                name=f'{name}',
                value=value,
                costs={"time": cost, "distance": 0., "fixed": cost},
                time_windows=make_windows(date, row['Интервал работы']),
                priority=priority, start=-1, end=-1
            )
            couriers[name] = courier

        else:
            couriers[name].time_windows.append(make_windows(date, row['Интервал работы'])[0])

    couriers = [courier for name, courier in couriers.items()]
    return couriers


def parse_depots(date: str, index: int, mapping: dict, address_mapping: dict, t_d, t_a) -> Tuple[int, Dict[str, Depot]]:
    """
    Parse depots data
    """
    logging.info('Parsing depots...')
    depots_data = pd.read_excel('./data/Склады.xlsx')
    depots = {}

    for i, row in depots_data.iterrows():
        lat, lng = float(row['Широта']), float(row['Долгота'])
        depot_loc, index = __add_point(mapping, index, lat, lng)
        name = row['Наименование'].replace(' ', '').replace('/', '-').replace('Мск,', '')
        address_mapping[(lat, lng)] = (name, name, name)
        load = t_d * 60 if 'Марьинарощасклад' else t_a * 60
        depot = Depot(name, depot_loc, load, load, make_windows(date, row['График работы'])[0])
        depots[name] = depot

    return index, depots


def parse_data(matrix_type: str, aver: float, address_mapping: Dict[Point, Tuple[str, str, str]],
               time_pharmacy, time_depot, type_weight, type_capacity, driver_weight, driver_capacity, delay):
    """ Main function for parsing data
    """
    logging.info('Parsing data...')

    courier_typing = {'Водитель': 'driver', 'Курьер': matrix_type}
    mapping, index = {}, 0

    index, date, orders = parse_orders(aver, index, mapping, delay)
    couriers = parse_couriers(date, courier_typing, type_weight, type_capacity, driver_weight, driver_capacity)
    index, depots = parse_depots(date, index, mapping, address_mapping, time_depot, time_pharmacy)

    logging.info(f'Couriers: {len(couriers)}')
    logging.info(f'Orders: {sum([len(tasks) for _, tasks in orders.items()])} to {len(orders)}')
    logging.info(f'Depots: {len(depots)}')
    logging.info(f'Orders to depot: {[len(tasks) for _, tasks in orders.items()]}')

    return orders, depots, couriers, mapping


def reindexing(depot: Depot, depot_id: str, global_revers: dict, tasks: Dict[str, List[Task]],
               address_mapping: Dict[Point, Tuple[str, str, str]]) -> Dict[Point, int]:
    """ Reindexing for tasks location
    """

    internal_mapping, index = {}, 0
    if len(tasks[depot_id]) > 10:
        tmp_loc = depot_loc = global_revers[depot.location]
        depot_loc, index = __add_point(internal_mapping, index, depot_loc[0], depot_loc[1])
        depot.location = depot_loc

        min_priority = min([task.priority for task in tasks[depot_id]])
        for task in tasks[depot_id]:
            task_loc = global_revers[task.location]
            task_loc, index = __add_point(internal_mapping, index, task_loc[0], task_loc[1])
            task.location = task_loc
            task.priority = task.priority if min_priority == 1 else 1

        courier_loc = (round(tmp_loc[0] + 5e-4, 6), round(tmp_loc[1], 6))
        address_mapping[courier_loc] = ('depot', 'depot', 'depot')
        __add_point(internal_mapping, index, courier_loc[0], courier_loc[1])

    return internal_mapping


def load_matrix(
        profiles: List[str],
        depots: Dict[str, Depot],
        global_revers: Dict,
        orders: Dict[str, List[Task]],
        address_mapping: Dict[Point, Tuple[str, str, str]]
) -> Tuple[Dict[str, List[Point]], Dict[str, dict], Dict[str, List[str]]]:
    """
    Load file matrix info and reindexing for tasks
    """

    points = {}
    internal_mappings = {}

    for i, (depot_id, depot) in enumerate(depots.items()):
        internal_mapping = reindexing(depot, depot_id, global_revers, orders, address_mapping)
        internal_mappings[depot_id] = internal_mapping
        points[depot_id] = [point for point in internal_mapping]

    files = defaultdict(list)
    for i, (depot_id, pts) in enumerate(points.items()):
        name = depot_id

        for profile in profiles:
            file = f'./new_matrices_1/{name}.{profile}.routing_matrix.json'
            pts = points[depot_id]

            dict(
                transport_complex=download_transport_complex,
                transport_simple=download_transport_simple,
                pedestrian=download_pedestrian,
                driver=download_driver,
                bicycle=download_bicycle,
            )[profile](file, pts)

            files[depot_id] += [file]

    return points, internal_mappings, files


def download_transport_simple(file, points: list):
    def return_checked(t, d: int):
        if t != 0 and 5 < d / t < 13:
            if t > 2 * 60 * 60:
                return d / 12, d
            elif d > 100 * 1000:
                return t, t * 12
            else:
                return d / 12, d
        return t, d

    p_dist, p_time = osrm_module.get_osrm_matrix(points, transport='foot')
    c_dist, c_time = osrm_module.get_osrm_matrix(points, transport='car')

    res_time = np.zeros(p_dist.shape)
    res_dist = np.zeros(p_dist.shape)

    res_time[p_time <= 15 * 60] = p_time[p_time <= res_time['time']]
    res_time[15 * 60 < p_time < 45 * 60] = p_time[15 * 60 < p_time < 45 * 60]

    travel_times, distances = [], []
    for i in range(len(points)):
        for j in range(len(points)):
            pt = p_dist[i][j]
            dtt, dd = return_checked(p_time[i][j], p_time[i][j])

            if pt <= 15 * 60:
                travel_times.append(int(pt))
                distances.append(int(pt))
            elif 15 * 60 < pt < 45 * 60:
                tt = int(min(dtt * 1.5, pt))
                travel_times.append(tt)
                distances.append(int(dd))
            else:
                tt = int(min(dtt * 2, pt))
                travel_times.append(tt)
                distances.append(int(dd))

    routing = {'profile': 'transport_simple', 'travelTimes': travel_times, 'distances': distances}

    with open(file, 'w') as f:
        ujson.dump(routing, f)
