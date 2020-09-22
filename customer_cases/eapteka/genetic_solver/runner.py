import math
import os
import uuid
from copy import deepcopy
from datetime import datetime
from typing import List, Dict, Tuple

import numba as nb
import numpy as np
import ujson
from herepy import RouteMode
from madrich.api_module import osrm_module, fake_module, here_module
from madrich.utils import to_array

from customer_cases.eapteka.genetic_solver.converter import generate_json, convert_json
from customer_cases.eapteka.genetic_solver.models import Task, Depot, Courier
from customer_cases.eapteka.genetic_solver.settings import OSRM_PEDESTRIAN, OSRM_DRIVER, DEBUG, HERE_KEY
from geo.martices.osrm import get_osrm_matrix

array = np.ndarray


def runner(tasks: List[Task], depot: Depot, couriers: List[Courier],
           profiles: List[str], distance: Dict[str, array], travel_time: Dict[str, array]):
    name = f'{uuid.uuid4()}'

    if not os.path.exists('./tmp'):
        os.mkdir('./tmp')

    solution_file = f'./tmp/{name}_solution.json'
    print('Generating Json...')
    problem_file, matrix_files = generate_json(name, profiles, tasks, depot, couriers, distance, travel_time)
    m = []
    for matrix in matrix_files:
        m.append('-m')
        m.append(matrix[1])
    print('Solving...')
    command = f'vrp-cli solve pragmatic {problem_file} --log {" ".join(m)} -o {solution_file}'
    os.system(command)
    solution = convert_json(solution_file)
    os.remove(problem_file)
    os.remove(solution_file)
    [os.remove(matrix_file[1]) for matrix_file in matrix_files]

    return solution


def multi_runner(tasks: Dict[str, List[Task]], depots: Dict[str, Depot], couriers: List[Courier],
                 mapping: Dict[Tuple[float, float], int]):
    # Сортируем, чтобы первыми были ранние склады
    couriers, depots = __sort(couriers, depots)

    profiles = ['pedestrian', 'driver']
    global_revers = {v: k for k, v in mapping.items()}
    solutions = []

    for i, (depot_id, depot) in enumerate(depots.items()):
        try:
            print('Problem:', depot_id, 'id:', i)
            print('Couriers:', len(couriers))
            print('Tasks:', len(tasks[depot_id]))

            if len(couriers) == 0:
                solution = {"unassigned": [{
                    "jobId": "all", "reasons": [{"code": 0, "description": "cannot find car for jobs"}]}]
                }
                solutions.append(solution)
                continue

            # Переиндексация
            internal_mapping = __reindexing(depot, depot_id, global_revers, tasks, couriers)

            # Загрузка матриц и запуск
            points = to_array([point for point in internal_mapping])
            if DEBUG:
                p_distance, p_travel_time = fake_module.get_matrix(points, ['distance', 'duration'])
                d_distance, d_travel_time = fake_module.get_matrix(points, ['distance', 'duration'])
                p_travel_time //= 500
                d_travel_time //= 500
            else:
                pts = to_array([(point[1], point[0]) for point in internal_mapping])
                p_distance, _ = osrm_module.get_matrix(pts, ['distance', 'duration'], host=OSRM_PEDESTRIAN)
                p_travel_time = p_distance / 1.5
                d_distance, _ = osrm_module.get_matrix(pts, ['distance', 'duration'], host=OSRM_DRIVER)
                d_travel_time = d_distance / 18

            if len(points) < 100:
                p_distance, p_travel_time, d_distance, d_travel_time = __get_matrix(depot, points)

            distance = {'pedestrian': p_distance, 'driver': d_distance}
            travel_time = {'pedestrian': p_travel_time, 'driver': d_travel_time}

            # Окна под склад сужаем у курьеров
            tmp_couriers = __cut_windows(couriers, depot)

            # Запуск
            solution = runner(tasks[depot_id], depot, tmp_couriers, profiles, distance, travel_time)
            solutions.append({'solution': solution, 'indexes': __get_index(internal_mapping)})
        except Exception as exc:
            print(exc, '\n')
            continue

        if not os.path.exists('./data'):
            os.mkdir('./data')
        with open('data/answer.json', 'w') as f:
            ujson.dump(solutions, f)

        # Удаляем использованных курьеров
        for tour in solution['tours']:
            type_id = tour['typeId']
            for j, courier in enumerate(couriers):
                if courier.type_id == type_id:
                    del couriers[j]
                    break

        print('Done:   ', depot_id, 'id:', i, '\n')

    return solutions


def __cut_windows(couriers: List[Courier], depot: Depot) -> List[Courier]:
    start_depot, end_depot = depot.time_window
    start_dt = datetime.strptime(start_depot, '%Y-%m-%dT%H:%M:%SZ')
    end_dt = datetime.strptime(end_depot, '%Y-%m-%dT%H:%M:%SZ')

    tmp_couriers = []
    for courier in couriers:
        tmp_courier = deepcopy(courier)

        for i in range(len(tmp_courier.time_windows)):
            start, end = tmp_courier.time_windows[i]
            start_t = datetime.strptime(start, '%Y-%m-%dT%H:%M:%SZ')
            end_t = datetime.strptime(end, '%Y-%m-%dT%H:%M:%SZ')

            tmp_courier.time_windows[i] = (start if start_dt <= start_t else start_depot,
                                           end if end_dt >= end_t else end_depot)

        tmp_couriers.append(tmp_courier)

    return tmp_couriers


def __get_index(internal_mapping):
    mapping = {}
    for point, index in internal_mapping.items():
        mapping[str(index)] = {'lat': point[0], 'lon': point[1]}
    return mapping


def __sort(couriers: List[Courier], depots: Dict[str, Depot]):
    couriers = sorted(couriers, key=lambda x: int(x.time_windows[0][0][11:13]))
    depots = {k: v for k, v in sorted(depots.items(), key=lambda x: x[1].time_window[0][11:13])}
    return couriers, depots


def __reindexing(depot: Depot, depot_id: str, global_revers: dict, tasks: dict, couriers: list) -> dict:
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

    for courier in couriers:
        courier_start_loc, index = add_point(index, tmp_loc[0] + 5e-4, tmp_loc[1] + 5e-4)
        courier_end_loc, index = add_point(index, tmp_loc[0] + 5e-4, tmp_loc[1] + 5e-4)
        courier.start = courier_start_loc
        courier.end = courier_end_loc

    return internal_mapping


def __get_matrices(points):
    matrix = __get_sinus(points)
    p_distance = matrix * 600 * 1.2
    d_distance = matrix * 600 * 1.5
    p_travel_time = p_distance / 2
    d_travel_time = d_distance / 3
    return p_distance, p_travel_time, d_distance, d_travel_time


@nb.njit
def __get_sinus(points):
    size = points.shape[0]
    matrix = np.zeros(shape=(size, size))
    for idx in range(0, size):
        for idy in range(idx + 1, size):
            lat1, lon1 = points[idx]
            lat2, lon2 = points[idy]
            d_lat = (lat2 - lat1) * math.pi / 180.0
            d_lon = (lon2 - lon1) * math.pi / 180.0

            # convert to radians
            lat1 = lat1 * math.pi / 180.0
            lat2 = lat2 * math.pi / 180.0

            # apply formulae
            a = (math.sin(d_lat / 2) ** 2 + (math.sin(d_lon / 2) ** 2) * math.cos(lat1) * math.cos(lat2))
            rad = 6371
            c = 2 * math.asin(math.sqrt(a))

            matrix[idx][idy] = matrix[idy][idx] = rad * c

    return matrix


def __get_matrix(depot, points):
    t = datetime.strptime(depot.time_window[0], '%Y-%m-%dT%H:%M:%SZ').timestamp()
    p = [RouteMode.fastest, RouteMode.pedestrian, RouteMode.traffic_enabled]
    d = [RouteMode.fastest, RouteMode.car, RouteMode.traffic_enabled]
    if len(points) < 100:
        p_distance, p_travel_time = here_module.get_matrix(points, p, t, HERE_KEY, ['distance', 'travelTime'])
        d_distance, d_travel_time = here_module.get_matrix(points, d, t, HERE_KEY, ['distance', 'travelTime'])
    else:
        # size = int(np.ceil(len(points) / 99))
        # for i in range(size):
        #     p_distance, p_travel_time = here_module.get_matrix(points, p, t, HERE_KEY, ['distance', 'travelTime'])
        #     d_distance, d_travel_time = here_module.get_matrix(points, d, t, HERE_KEY, ['distance', 'travelTime'])
        assert False

    return p_distance, p_travel_time, d_distance, d_travel_time
