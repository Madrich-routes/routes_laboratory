import os
from pathlib import Path
from typing import List

import ujson

from madrich.models.rich_vrp.agent import Agent
from madrich.models.rich_vrp.problem import RichVRPProblem
from madrich.solvers.vrp_cli.converters import convert_tw, ts_to_rfc
from madrich.utils.types import Matrix


def dump_jobs(problem: RichVRPProblem) -> List[dict]:
    """Получаем заформаченные заказы для problem.json (pragmatic format)"""
    jobs_dicts = []
    for job in problem.jobs:
        tmp = {
            'id': str(job.id),
            'deliveries': [
                {
                    'places': [
                        {
                            'location': {'index': problem.matrix.index(job)},
                            'duration': int(job.delay),
                            'times': convert_tw(job.time_windows),
                        }
                    ],
                    'demand': job.capacity_constraints,
                }
            ],
        }
        jobs_dicts.append(tmp)

    return jobs_dicts


def dump_shifts(agent: Agent, problem: RichVRPProblem) -> List[dict]:
    """Все смены загоняем в pragmatic формат"""
    return [{
        'start': {
            'earliest': ts_to_rfc(time_window[0]),
            'location': {'index': problem.matrix.index(problem.depot)},
        },
        'end': {
            'latest': ts_to_rfc(time_window[1]),
            'location': {'index': problem.matrix.index(problem.depot)},
        },
        'reloads': [
            {
                'location': {'index': problem.matrix.index(problem.depot)},
                'duration': int(problem.depot.delay),
            }
        ],
    } for time_window in agent.time_windows]


def dump_vehicles(problem: RichVRPProblem) -> List[dict]:
    """Дампим агентов в pragmatic формат"""
    agents_dict = []
    for agent in problem.agents:
        # проверим, что демо в списке депо, который курьер может посещать
        if problem.depot.id not in [depot.id for depot in agent.compatible_depots]:
            continue
        # не передаем fixed в vrp-cli, т.к. сломается глобальная статистика при вызове агента в нескольких депо
        tmp = {
            'typeId': str(agent.id),
            'vehicleIds': [str(agent.id)],
            'profile': agent.profile,
            'costs': agent.costs,
            'shifts': dump_shifts(agent, problem),
            'capacity': agent.capacity_constraints,
        }
        agents_dict.append(tmp)
    return agents_dict


def dump_problem(path: Path, directory: Path, problem: RichVRPProblem):
    """Дампим проблему в pragmatic формат и сохраняем в директорию по заданному пути"""
    jobs_dict = dump_jobs(problem)
    agents_dict = dump_vehicles(problem)

    profiles = [
        {'name': profile, 'type': f'{profile}_profile'} for profile, geometry in problem.matrix.geometries.items()
    ]
    problem = {
        'plan': {'jobs': jobs_dict},
        'fleet': {'vehicles': agents_dict, 'profiles': profiles},
    }

    os.makedirs(directory, exist_ok=True)
    with open(path, 'w') as f:
        ujson.dump(problem, f)


def dump_matrix(profile: str, distance_matrix: Matrix, time_matrix: Matrix) -> str:
    """Получаем pragmatic представление матрицы расстояний.

    Parameters
    ----------
    profile : профайл (например driver, foot, transport)
    distance_matrix : матрица расстояний
    time_matrix : матрица времениы

    Returns
    -------
    Строковое представление в pragmatic
    """
    size = len(distance_matrix)
    travel_times, distances = [], []
    for i in range(size):
        for j in range(size):
            travel_times.append(int(time_matrix[i][j]))
            distances.append(int(distance_matrix[i][j]))

    obj = {"profile": profile, "travelTimes": travel_times, "distances": distances}
    return ujson.dumps(obj)


def dump_matrices(path: Path, problem: RichVRPProblem):
    """Дампим все матрицы для всех профилей и сохраняем в заданную директории"""
    os.makedirs(path, exist_ok=True)
    matrix_files = {
        profile: dump_matrix(profile, geometry["dist_matrix"], geometry["time_matrix"])
        for profile, geometry in problem.matrix.geometries.items()
    }
    res = []
    for profile, matrix in matrix_files.items():
        matrix_path = path / f'{profile}.json'
        res.append(matrix_path)
        with open((path / f'{profile}.json'), "w") as f:
            f.write(matrix)
    return res
