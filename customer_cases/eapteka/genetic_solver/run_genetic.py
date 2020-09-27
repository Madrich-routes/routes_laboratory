from copy import deepcopy
from datetime import datetime
from typing import Tuple, List

from customer_cases.eapteka.genetic_solver.models import Courier, Depot


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
                end_t = f'{tokens[i + 1]}' if 9 < int(tokens[i + 1][:2]) < 24 else f'23:59'
                end = f'{date}T{end_t}:00Z'
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


def __check_point(lat, lon):
    assert 54.966833 < lat < 56.393109, f'bad point {lat}'
    assert 36.1686653 < lon < 38.9163203, f'bad point {lon}'


def __cut_windows(couriers: List[Courier], depot: Depot) -> List[Courier]:
    start_depot, end_depot = depot.time_window
    start_dt = datetime.strptime(start_depot, '%Y-%m-%dT%H:%M:%SZ')
    end_dt = datetime.strptime(end_depot, '%Y-%m-%dT%H:%M:%SZ')

    tmp_couriers = []
    for courier in couriers:
        tmp_courier = deepcopy(courier)

        tw = []
        for i in range(len(tmp_courier.time_windows)):
            start, end = tmp_courier.time_windows[i]
            start_t = datetime.strptime(start, '%Y-%m-%dT%H:%M:%SZ')
            end_t = datetime.strptime(end, '%Y-%m-%dT%H:%M:%SZ')

            if start_t <= start_dt <= end_t <= end_dt or start_dt <= start_t <= end_dt <= end_t or \
                    start_dt <= start_t <= end_t <= end_dt or start_t <= start_dt <= end_dt <= end_t:
                tw.append((start if start_dt <= start_t else start_depot, end if end_dt >= end_t else end_depot))

        if tw:
            tmp_courier.time_windows = tw
            tmp_couriers.append(tmp_courier)

    return tmp_couriers


def __get_index(internal_mapping):
    mapping = {}
    for point, index in internal_mapping.items():
        mapping[str(index)] = {'lat': point[0], 'lon': point[1]}
    return mapping
