import logging
import os
from typing import Dict, List, Tuple

from customer_cases.eapteka.genetic_solver.converter import convert_json, generate_problem
from customer_cases.eapteka.genetic_solver.models import Courier, Depot, Task

Point = Tuple[float, float]


def runner(
        tasks: List[Task],
        depot_id: str,
        depot: Depot,
        couriers: List[Courier],
        profiles: List[str],
        files: Dict,
        max_time: int = 3 * 3600,  # максимальное время работы
        max_generations: int = 30_000,  # максимальное количество поколений
        variation_generations: int = 100,  # на скольких поколениях измеряется cost_variation
        min_variation: int = 0.1,  # минимальная вариация (критерий остановки)
):
    """Вызываем солвер vrp_cli.

    Документация: https://reinterpretcat.github.io/vrp/getting-started/solver.html
    """
    name = f'{depot_id}'

    if not os.path.exists('./tmp'):
        os.mkdir('./tmp')

    solution_file = f'./tmp/{name}_solution.json'
    logging.info('Generating Json...')
    problem_file = generate_problem(name, profiles, tasks, depot, couriers)
    m = []
    for matrix in files[depot_id]:
        m.append('-m')
        m.append(matrix)

    return solution
