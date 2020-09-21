import os
import uuid
from typing import List, Dict

import numpy as np

from customer_cases.eapteka.genetic_solver.converter import generate_json, convert_json
from customer_cases.eapteka.genetic_solver.models import Task, Depot, Courier

array = np.ndarray


def runner(tasks: List[Task], depot: Depot, couriers: List[Courier],
           profiles: List[str], distance: Dict[str, array], travel_time: Dict[str, array]):
    name = f'{uuid.uuid4()}'

    if not os.path.exists('./data'):
        os.mkdir('data')

    solution_file = f'./data/{name}_solution.json'
    problem_file, matrix_files = generate_json(name, profiles, tasks, depot, couriers, distance, travel_time)
    m = []
    for matrix in matrix_files:
        m.append('-m')
        m.append(matrix[1])
    command = f'vrp-cli solve pragmatic {problem_file} {" ".join(m)} -o {solution_file}'
    os.system(command)
    solution = convert_json(solution_file)

    os.remove(problem_file)
    os.remove(solution_file)
    [os.remove(matrix_file[1]) for matrix_file in matrix_files]

    print(solution)

    return solution


def multi_runner(tasks: Dict[str, List[Task]], depots: Dict[str, Depot], couriers: List[Courier],
                 profiles: List[str], distance: Dict[str, array], travel_time: Dict[str, array]) -> List[dict]:
    solutions = []

    for i, (depot_id, depot) in enumerate(depots.items()):

        if len(couriers) == 0:
            solution = {"unassigned": [{
                "jobId": "all", "reasons": [{"code": 0, "description": "cannot find car for jobs"}]}]
            }
            solutions.append(solution)
            continue

        solution = runner(tasks[depot_id], depot, couriers, profiles, distance, travel_time)
        solutions.append(solution)

        print(solution)

    return solutions
