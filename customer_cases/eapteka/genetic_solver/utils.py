from copy import deepcopy
from datetime import datetime, timedelta
from typing import Tuple, List, Optional

from customer_cases.eapteka.genetic_solver.models import Courier, Depot


def make_windows_orders(date: str, interval: str) -> List[Tuple[str, str]]:
    """ Makes time windows for orders
    """
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
    """ Makes time windows for couriers and depots
    """
    if interval == 'круглосуточно':
        return [(f'{date}T00:00:00Z', f'{date}T23:59:59Z')]
    start, end = interval.split('-')
    start = f'0{int(start)}:00' if int(start) < 10 else f'{start}:00'
    if int(end) < 10:
        end = f'0{int(end)}:00'
    else:
        end = f'{end}:00' if int(end) != 24 else f'23:59'
    return [(f'{date}T{start}:00Z', f'{date}T{end}:00Z')]


def check_point(lat, lon):
    """ Check that point in some borders near Moscow
    """
    assert 54.966833 < lat < 56.393109, f'bad point {lat}'
    assert 36.1686653 < lon < 38.9163203, f'bad point {lon}'


def cut_windows(couriers: List[Courier], depot: Depot) -> List[Courier]:
    """ Adapt couriers time windows for depot; returns new list of couriers
    """
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


def get_index(internal_mapping):
    """ Return location dict by index from mapping
    """
    mapping = {}
    for point, index in internal_mapping.items():
        mapping[str(index)] = {'lat': point[0], 'lon': point[1]}
    return mapping


def send_courier(courier: Courier, start_time: str, end_time: str) -> Optional[Courier]:
    change_depot = datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%SZ') + timedelta(minutes=40)
    relocate_from = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%SZ') - timedelta(minutes=40)

    change_depot_with = change_depot + timedelta(minutes=5)
    relocate_from_with = relocate_from - timedelta(minutes=5)

    tmp_courier = deepcopy(courier)
    tw = []
    for i, time_windows in enumerate(tmp_courier.time_windows):
        end_windows = datetime.strptime(time_windows[1], '%Y-%m-%dT%H:%M:%SZ')
        start_windows = datetime.strptime(time_windows[0], '%Y-%m-%dT%H:%M:%SZ')

        if relocate_from_with <= change_depot_with <= start_windows <= end_windows:
            tw.append(time_windows)

        if start_windows <= end_windows <= relocate_from_with <= change_depot_with:
            tw.append(time_windows)

        if relocate_from_with <= start_windows <= change_depot_with <= end_windows:
            window = start_windows if start_windows > change_depot else change_depot
            tw.append((window.strftime("%Y-%m-%dT%H:%M:%SZ"), time_windows[1]))

        if start_windows <= relocate_from_with <= end_windows <= change_depot_with:
            window = end_windows if end_windows < relocate_from else relocate_from
            tw.append((time_windows[0], window.strftime("%Y-%m-%dT%H:%M:%SZ")))

        if start_windows <= relocate_from_with <= change_depot_with <= end_windows:
            start = start_windows if start_windows > change_depot else change_depot
            end = end_windows if end_windows < relocate_from else relocate_from

            tw.append((start.strftime("%Y-%m-%dT%H:%M:%SZ"), time_windows[1]))
            tw.append((time_windows[0], end.strftime("%Y-%m-%dT%H:%M:%SZ")))

    if tw:
        tw = sorted(tw, key=lambda x: int(x[0][11:13]))
        tmp_courier.time_windows = tw
        return tmp_courier

    return None


def add_courier(data, name, depot, start_time, end_time, distance, duration, points):
    data['name'].append(name)
    data['depot'].append(depot)
    data['start_time'].append(start_time)
    data['end_time'].append(end_time)
    data['distance'].append(distance)
    data['duration'].append(duration)
    data['points'].append(points)


def add_depot(data, name, distance, duration):
    data['name'].append(name)
    data['distance'].append(distance)
    data['duration'].append(duration)


def add_tour(data, address, before, corrected, loc, arrival, departure, activity, weight, capacity):
    data['address'].append(address)
    data['before'].append(before)
    data['corrected'].append(corrected)
    data['loc'].append(loc)
    data['arrival'].append(arrival)
    data['departure'].append(departure)
    data['activity'].append(activity)
    data['weight'].append(weight)
    data['capacity'].append(capacity)