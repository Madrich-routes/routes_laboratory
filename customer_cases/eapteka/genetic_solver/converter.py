import json
import os
from typing import Tuple, List, Dict

import numpy as np

from customer_cases.eapteka.genetic_solver.models import Task, Depot, Courier

Point = Tuple[float, float]
array = np.ndarray


def convert_json(file: str):
    with open(file, 'r') as f:
        solution = json.load(f)
    return solution


def generate_json(name: str, profiles: List[str], tasks: List[Task], depot: Depot, couriers: List[Courier],
                  distance_matrix: Dict[str, array], time_matrix: Dict[str, array]):
    matrix_file = __generate_matrix(name, profiles, distance_matrix, time_matrix)
    problem_file = __generate_problem(name, profiles, tasks, depot, couriers)
    return problem_file, matrix_file


def __generate_matrix(name: str, profiles: List[str], distance_matrix: Dict[str, array], time_matrix: Dict[str, array]):
    files: List[Tuple[str, str]] = []
    size = len(distance_matrix[profiles[0]])

    if not os.path.exists('./data'):
        os.mkdir('data')

    for profile in profiles:

        travel_times, distances = [], []
        for i in range(size):
            for j in range(size):
                travel_times.append(int(time_matrix[profile][i][j]))
                distances.append(int(distance_matrix[profile][i][j]))

        routing = {'profile': profile, 'travelTimes': travel_times, 'distances': distances}

        file = f'./data/{name}.{profile}.routing_matrix.json'
        with open(file, 'w') as f:
            json.dump(routing, f)
        files.append((profile, file))

    return files


def __generate_problem(name: str, profiles: List[str], tasks: List[Task], depot: Depot, couriers: List[Courier]) -> str:
    jobs = []
    for i, task in enumerate(tasks):
        job = {
            'id': f'job_{i}',
            'deliveries': [{
                'places': [{'location': {'index': task.location}, 'duration': task.delay, 'times': task.time_windows}],
                'demand': task.value,
            }],
            'priority': task.priority
        }
        jobs.append(job)

    executors = []
    for i, courier in enumerate(couriers):
        executor = {
            'typeId': courier.type_id,
            'vehicleIds': [courier.name],
            'profile': courier.profile,
            'costs': courier.costs,
            'shifts': [{
                'start': {'earliest': time_window[0], 'location': {'index': courier.start}},
                'end': {'latest': time_window[1], 'location': {'index': courier.end}},
                'reloads': [{'location': {'index': depot.location}, 'duration': depot.reload}],
                'depots': [{'location': {'index': depot.location}, 'duration': depot.load}]
            } for time_window in courier.time_windows],
            'capacity': courier.value,
        }
        executors.append(executor)

    profiles = [{'name': profile, 'type': f'{profile}_profile'} for profile in profiles]
    problem = {'plan': {'jobs': jobs}, 'fleet': {'vehicles': executors, 'profiles': profiles}}

    if not os.path.exists('./data'):
        os.mkdir('data')

    file = f'./data/{name}.json'
    with open(file, 'w') as f:
        json.dump(problem, f)
    return file
