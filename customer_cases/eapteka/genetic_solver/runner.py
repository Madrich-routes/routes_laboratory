import os
from typing import Tuple, List

from customer_cases.eapteka.genetic_solver.converter import generate_problem, convert_json
from customer_cases.eapteka.genetic_solver.models import Task, Courier, Depot

Point = Tuple[float, float]


def runner(tasks: List[Task], depot_id: str, depot: Depot, couriers: List[Courier], profiles: List[str], files: dict):
    name = f'{depot_id}'

    if not os.path.exists('./tmp'):
        os.mkdir('./tmp')

    solution_file = f'./tmp/{name}_solution.json'
    print('Generating Json...')
    problem_file = generate_problem(name, profiles, tasks, depot, couriers)
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
