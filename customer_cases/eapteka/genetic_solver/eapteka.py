import math
import os
from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timedelta
from typing import Tuple, List

import pandas as pd
import ujson
from transliterate import translit

from customer_cases.eapteka.genetic_solver.converter import generate_json, convert_json
from customer_cases.eapteka.genetic_solver.models import Task, Courier, Depot
from customer_cases.eapteka.genetic_solver.run_genetic import make_windows_orders, __check_point, make_windows, \
    __cut_windows, __get_index


def parse_data(matrix_type: str, aver: float, address_mapping: dict, address_before: dict, address_corrected: dict):
    courier_typing = {'Водитель': 'driver', 'Курьер': matrix_type}
    mapping, index = {}, 0

    def add_point(idx: int, lt: float, ln: float) -> Tuple[int, int]:
        point = (lt, ln)
        if point not in mapping:
            mapping[point] = idx
            idx += 1
        return mapping[point], idx

    orders, errors = defaultdict(list), 0
    orders_inf = pd.read_excel('./data/Заказы_13.xlsx')
    orders_loc = pd.read_excel('./data/update_3.xlsx')

    date = orders_inf.iloc[0]['ДатаДоставки']
    date = f'{date[6:10]}-{date[3:5]}-{date[0:2]}'

    for i, row in orders_inf.iterrows():
        try:
            lat, lng = orders_loc['lat'][i], orders_loc['lng'][i]
            __check_point(lat, lng)
            point_index, index = add_point(index, lat, lng)
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
            orders[storage].append(Task(point_index, time_windows, 5 * 60, value, priority))

        except Exception as exc:
            errors += 1
            if not math.isnan(row['Приоритет']):
                lat, lng = orders_loc['lat'][i], orders_loc['lng'][i]
                print(i, lat, lng, orders_loc['place'][i])
                print(exc)

    print('Errors ignored:', errors, '\n')

    couriers = {}
    couriers_data = pd.read_excel('./data/Курьеры_13.xlsx')
    for i, row in couriers_data.iterrows():
        name = translit(f'{row["Сотрудник"]}', 'ru', reversed=True)
        if name not in couriers:
            priority = int(row['Приоритет'] if not math.isnan(row['Приоритет']) else 2)
            cost = int(row['Стоимость 1 заказа']) if priority == 1 else int(row['Стоимость 1 заказа'])
            profile = courier_typing[row['Должность']]
            value = [200 * 100, 400 * 100] if profile == 'driving' else [15 * 100, 40 * 100]
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

    depots_data = pd.read_excel('./data/Склады.xlsx')
    depots = {}
    for i, row in depots_data.iterrows():
        lat, lng = float(row['Широта']), float(row['Долгота'])
        depot_loc, index = add_point(index, lat, lng)
        name = row['Наименование'].replace(' ', '').replace('/', '-').replace('Мск,', '')
        address_mapping[(lat, lng)] = name
        address_before[(lat, lng)] = name
        address_corrected[(lat, lng)] = name
        load = 10 * 60 if 'Марьинарощасклад' else 5 * 60
        depot = Depot(name, depot_loc, load, load, make_windows(date, row['График работы'])[0])
        depots[name] = depot

    print('Couriers:', len(couriers))
    print('Orders:', sum([len(tasks) for _, tasks in orders.items()]), 'to', len(orders))
    print('Depots:', len(depots))
    print('Orders to depot:', [len(tasks) for _, tasks in orders.items()])

    return orders, depots, couriers, mapping


def reindexing(depot: Depot, depot_id: str, global_revers: dict, tasks: dict,
               address_mapping: dict, address_before: dict, address_corrected: dict) -> dict:
    internal_mapping, index = {}, 0

    def add_point(idx: int, lat: float, lon: float) -> Tuple[int, int]:
        point = (lat, lon)
        if point not in internal_mapping:
            internal_mapping[point] = idx
            idx += 1
        return internal_mapping[point], idx

    tmp_loc = depot_loc = global_revers[depot.location]
    depot_loc, index = add_point(index, depot_loc[0], depot_loc[1])
    depot.location = depot_loc

    min_priority = min([task.priority for task in tasks[depot_id]])
    for task in tasks[depot_id]:
        task_loc = global_revers[task.location]
        task_loc, index = add_point(index, task_loc[0], task_loc[1])
        task.location = task_loc
        task.priority = task.priority if min_priority == 1 else 1

    courier_loc = (round(tmp_loc[0] + 5e-4, 6), round(tmp_loc[1], 6))
    address_mapping[courier_loc] = 'depot'
    address_before[courier_loc] = 'depot'
    address_corrected[courier_loc] = 'depot'
    add_point(index, courier_loc[0], courier_loc[1])

    return internal_mapping


def download_matrix(profiles: list, depots: dict, global_revers: dict, orders: dict,
                    address_mapping: dict, address_before: dict, address_corrected: dict):
    points = {}
    internal_mappings = {}

    for i, (depot_id, depot) in enumerate(depots.items()):
        internal_mapping = reindexing(depot, depot_id, global_revers, orders,
                                      address_mapping, address_before, address_corrected)

        internal_mappings[depot_id] = internal_mapping
        points[depot_id] = [point for point in internal_mapping]

    files = defaultdict(list)
    for i, (depot_id, pts) in enumerate(points.items()):
        name = depot_id
        for profile in profiles:
            file = f'./tmp/{name}.{profile}.routing_matrix.json'
            files[depot_id].append(file)

    return points, internal_mappings, files


def runner(tasks: List[Task], depot_id: str, depot: Depot, couriers: List[Courier], profiles: List[str], files: dict):
    name = f'{depot_id}'

    if not os.path.exists('./tmp'):
        os.mkdir('./tmp')

    solution_file = f'./tmp/{name}_solution.json'
    print('Generating Json...')
    problem_file = generate_json(name, profiles, tasks, depot, couriers)
    m = []
    for matrix in files[depot_id]:
        m.append('-m')
        m.append(matrix)
    print('Solving...')
    command = f'vrp-cli solve pragmatic {problem_file} --log {" ".join(m)} -o {solution_file}'
    os.system(command)
    solution = convert_json(solution_file)
    os.remove(problem_file)
    os.remove(solution_file)

    return solution


def send_courier(courier, start_time, end_time):
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


def get_solution(depots: dict, couriers: list, orders: dict, internal_mappings: dict, files: dict, profiles: list,
                 address_mapping: dict, address_before: dict, address_corrected: dict):
    solutions = {}
    all_points = 0
    couriers_output = defaultdict(list)
    depots_output = defaultdict(list)
    tours = {}

    for i, (depot_id, depot) in enumerate(depots.items()):
        print('\n')
        print('Problem:', depot_id, 'id:', i)
        print('Couriers:', len(couriers))
        print('Orders:', len(orders[depot_id]) - 2)

        courier_loc = 0
        for point in internal_mappings[depot_id]:
            courier_loc = internal_mappings[depot_id][point]
        revers_internal_mapping = {v: k for k, v in internal_mappings[depot_id].items()}

        for courier in couriers:
            courier.start = courier_loc
            courier.end = courier_loc

        tmp_couriers = __cut_windows(couriers, depot)

        solution = runner(orders[depot_id], depot_id, depot, tmp_couriers, profiles, files)
        solutions[depot_id] = {'solution': solution, 'indexes': __get_index(internal_mappings[depot_id])}

        print('Not Solved', 0 if 'unassigned' not in solution else len(solution['unassigned']))

        statistic = solution['statistic']
        add_depot(depots_output, depot_id, statistic['distance'], statistic['duration'])
        names = []
        st = 0

        for tour in solution['tours']:
            name = tour['vehicleId']
            points = len(tour['stops'])

            if points - 3 == 0:
                continue

            st += points

            start_time = tour['stops'][0]['time']['arrival']
            end_time = tour['stops'][-1]['time']['departure']
            duration = tour['statistic']['duration']
            distance = tour['statistic']['distance']

            tour_data = defaultdict(list)
            for j in range(0, points):
                point = tour['stops'][j]
                arrival = point['time']['arrival']
                departure = point['time']['departure']
                activity = point['activities'][0]['type']

                if activity != 'delivery':
                    points -= 1
                    st -= 1

                weight, capacity = [0, 0] if activity == 'departure' else point['load']
                loc = revers_internal_mapping[point['location']['index']]
                address = address_mapping[(loc[0], loc[1])]
                was = address_before[(loc[0], loc[1])]
                corrected = address_corrected[(loc[0], loc[1])]
                add_tour(tour_data, address, was, corrected, loc, arrival, departure, activity, weight, capacity)

            add_courier(couriers_output, name, depot_id, start_time, end_time, distance, duration, points)
            tours[f'{name}{depot_id}'] = tour_data
            names.append((name, start_time, end_time))

        sv = 0
        tmp_couriers = []
        for name, start_time, end_time in names:
            for j, courier in enumerate(couriers):
                if courier.name == name:
                    tmp = send_courier(courier, start_time, end_time)
                    if tmp is not None:
                        tmp_couriers.append(tmp)
                        sv += 1
                    del couriers[j]
                    break
        couriers += tmp_couriers

        all_points += st
        print('Solved:', st)
        print('Couriers:', len(names))
        print('Saved:', sv)

    print('Solved:', all_points)

    print('Writing...')

    pd.DataFrame.from_dict(couriers_output).to_csv("couriers.csv", index=False)
    pd.DataFrame.from_dict(depots_output).to_csv("depot.csv", index=False)

    for name, tour in tours.items():
        pd.DataFrame.from_dict(tour).to_csv(f"./couriers/{name}.csv", index=False)

    with open('answer.json', 'w') as f:
        ujson.dump(solutions, f)

    print('\nDone')
