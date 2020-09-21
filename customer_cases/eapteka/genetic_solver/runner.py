import os
import uuid
from typing import List, Dict, Tuple

import numpy as np
from madrich.api_module import fake_module
from madrich.utils import to_array

from customer_cases.eapteka.genetic_solver.converter import generate_json, convert_json
from customer_cases.eapteka.genetic_solver.models import Task, Depot, Courier

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
    command = f'vrp-cli solve pragmatic {problem_file} {" ".join(m)} -o {solution_file}'
    os.system(command)
    solution = convert_json(solution_file)
    os.remove(problem_file)
    os.remove(solution_file)
    [os.remove(matrix_file[1]) for matrix_file in matrix_files]

    return solution


def multi_runner(tasks: Dict[str, List[Task]], depots: Dict[str, Depot], couriers: List[Courier],
                 mapping: Dict[Tuple[float, float], int]):

    couriers, depots = __sort(couriers, depots)

    profiles = ['pedestrian', 'driver']
    global_revers = {v: k for k, v in mapping.items()}
    solutions = []

    for i, (depot_id, depot) in enumerate(depots.items()):
        print('Problem:', depot_id, 'id:', i)

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
        # TODO: real module
        p_distance, p_travel_time = fake_module.get_matrix(points, ['distance', 'duration'])
        d_distance, d_travel_time = fake_module.get_matrix(points, ['distance', 'duration'])
        p_travel_time //= 1000
        d_travel_time //= 1000

        distance = {'pedestrian': p_distance, 'driver': d_distance}
        travel_time = {'pedestrian': p_travel_time, 'driver': d_travel_time}

        # Запуск
        solution = runner(tasks[depot_id], depot, couriers, profiles, distance, travel_time)
        solutions.append({'solution': solution, 'indexes': {v: k for k, v in internal_mapping.items()}})

        # Удаляем использованных курьеров
        for tour in solution['tours']:
            type_id = tour['typeId']
            for j, courier in enumerate(couriers):
                if courier.type_id == type_id:
                    del couriers[j]
                    break

        print('Done:   ', depot_id, 'id:', i, '\n')

    return solutions


def __sort(couriers, depots):
    couriers = sorted(couriers, key=lambda x: int(x.time_windows[0][0][11:13]))
    depots = {k: v for k, v in sorted(depots.items(), key=lambda x: x[1].time_window[0][11:13])}
    return couriers, depots


def __reindexing(depot, depot_id, global_revers, tasks, couriers) -> dict:
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
