import os
from pathlib import Path
from typing import List

import ujson

from models.rich_vrp import Job, Agent, Depot
from models.rich_vrp.problem import RichVRPProblem
from utils.types import Matrix


def dump_jobs(jobs: List[Job]) -> List[dict]:
    jobs_dicts = []
    for job in jobs:
        tmp = {
            'id': job.id,
            'deliveries': [{
                'places': [{'location': {'index': job.},
                            'duration': job.delay,
                            'times': job.}],
                'demand': job.capacity_constraints
            }]
        }
        jobs_dicts.append(tmp)

    return jobs_dicts


def dump_vehicles(depot: Depot, agents: List[Agent]) -> List[dict]:
    agents_dict = []
    for agent in agents:
        tmp = {
            'typeId': agent.id,
            'vehicleIds': [agent.name],
            'profile': agent.profile,
            'costs': agent.costs,
            'shifts': [{
                'start': {'earliest': agent., 'location': {'index': depot.}},
                'end': {'latest': agent., 'location': {'index': depot.}},
                'reloads': [{'location': {'index': depot.}, 'duration': depot.delay}],
                'dispatch': [{'location': {'index': depot.}, 'duration': depot.delay}]
            }],
            'capacity': agent.capacity_constraints
        }
        agents_dict.append(tmp)
    return agents_dict


def dump_problem(path: Path, problem: RichVRPProblem):
    jobs_dict = dump_jobs(problem.jobs)
    agents_dict = dump_vehicles(problem.depot, problem.agents)

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


def dump_matrices(path: Path):
    os.makedirs(path, exist_ok=True)
    matrix_files = [profile: dump_matrix() for profile in profiles]
    for profile, matrix in matrix_files:
        with open((path / f'{profile}.json'), "w") as f:
            f.write(matrix)
