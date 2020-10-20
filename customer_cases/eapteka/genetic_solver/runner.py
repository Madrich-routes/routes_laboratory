import logging
import os
from typing import Tuple, List, Dict

from customer_cases.eapteka.genetic_solver.converter import generate_problem, convert_json
from customer_cases.eapteka.genetic_solver.models import Task, Courier, Depot

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
        variation_generations: int = 500,  # на скольких поколениях измеряется cost_variation
        min_variation: int = 0.03,  # минимальная вариация (критерий остановки)
):
    """
    Вызываем солвер vrp_cli.
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

    logging.info('Solving...')
    command = ' '.join([
        f'vrp-cli solve',  # вызываем решалку
        f'pragmatic {problem_file}',  # файл, в котором сфорумлирована проблемаы
        f'{" ".join(m)}',  # матрицы расстояний
        f'-o {solution_file}',  # куда писать результат
        f'--log',  # показывать лог на экране
        f'--max-time={max_time}',  # максимальное время работы
        f'--max-generations={max_generations}',  # максимальное количетсво поколений оптимизации
        # насколько медленно нужно оптимизировать, чтобы перестать
        f'--cost-variation={variation_generations},{min_variation}',
        # f'--geo-json=<filename>'
        # f'-i <initial_solution>',
   ])
    os.system(command)
    solution = convert_json(solution_file)
    os.remove(problem_file)
    os.remove(solution_file)

    return solution
