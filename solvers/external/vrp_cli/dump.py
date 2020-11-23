import os
from pathlib import Path
from typing import List

import ujson

from models.rich_vrp import Job, Agent, Depot
from models.rich_vrp.problem import RichVRPProblem
from utils.types import Matrix


def ts_to_rfc(ts: int) -> str:
    """Конвертируем unix timestamp в RFC3339 . В pragmatic время представлено в таком формате.
    Добавлена поправка для Windows на 86400, т.к. минимальный Unix timestamp 86400
    >>> ts_to_rfc(0)
    '1970-01-01T03:00:00Z'
    Parameters
    ----------
    ts : Unix timestamp
    Returns
    -------
    Время в формате RFC3339  в UTC таймзоне c Z на конце.
    """
    return datetime.fromtimestamp(ts + 86400).isoformat() + "Z"


def convert_tw(time_windows: List[Tuple[int, int]]) -> List[Tuple[str, str]]:
    """Конвретируем временное окно из таймстампов в RFC3339.
    >>> convert_tw([(0, 0)])
    [('1970-01-01T03:00:00Z', '1970-01-01T03:00:00Z')]
    Parameters
    ----------
    time_windows : Лист временных окон в unix timestamp
    Returns
    -------
    Лист временных окон в iso
    """
    return [(ts_to_rfc(tw[0]), ts_to_rfc(tw[1])) for tw in time_windows]


def dump_jobs(problem: RichVRPProblem) -> List[dict]:
    jobs_dicts = []
    for job in problem.jobs:
        tmp = {
            'id': job.id,
            'deliveries': [{
                'places': [{'location': {'index': problem.matrix.index(job)},
                            'duration': job.delay,
                            'times': convert_tw(job.time_windows)}],
                'demand': job.capacity_constraints
            }]
        }
        jobs_dicts.append(tmp)

    return jobs_dicts


def dump_vehicles(depot: Depot, agents: List[Agent]) -> List[dict]:
    agents_dict = []
    for agent in problem.agents:
        tmp = {
            'typeId': agent.id,
            'vehicleIds': [agent.name],
            'profile': agent.profile,
            'costs': agent.costs,
            'shifts': [{
                'start': {
                    'earliest': ts_to_rfc(agent.time_windows[0][0]),
                    'location': {'index': problem.matrix.index(problem.depot)}
                },
                'end': {
                    'latest': ts_to_rfc(agent.time_windows[-1][-1]),
                    'location': {'index': problem.matrix.index(problem.depot)}
                },
                'reloads': [{
                    'location': {'index': problem.matrix.index(problem.depot)}, 'duration': problem.depot.delay
                }],
                'dispatch': [{
                    'location': {'index': problem.matrix.index(problem.depot)}, 'duration': problem.depot.delay
                }]
            }],
            'capacity': agent.capacity_constraints
        }
        agents_dict.append(tmp)
    return agents_dict


def dump_problem(path: Path, problem: RichVRPProblem):
    jobs_dict = dump_jobs(problem)
    agents_dict = dump_vehicles(problem)

    profiles = [{'name': profile, 'type': f'{profile}_profile'} for profile in profiles]
    problem = {'plan': {'jobs': jobs_dict}, 'fleet': {'vehicles': agents_dict, 'profiles': profiles}}

    os.makedirs(path, exist_ok=True)
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

    obj = {"profile": profile, "travelTimes": time_matrix, "distances": distance_matrix}
    return ujson.dumps(obj)


def dump_matrices(path: Path, problem: RichVRPProblem):
    os.makedirs(path, exist_ok=True)
    matrix_files = [profile: dump_matrix(profile, geometry["dist_matrix"], geometry["time_matrix"]) for profile, geometry in problem.matrix.geometries.items()]
    for profile, matrix in matrix_files:
        with open((path / f'{profile}.json'), "w") as f:
            f.write(matrix)
