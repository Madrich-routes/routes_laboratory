from random import randint
from typing import List, Tuple

import numpy as np

from models.rich_vrp.agent import Agent
from models.rich_vrp.depot import Depot
from models.rich_vrp.job import Job
from solvers.external.vrp_cli.converters import str_to_ts, to_list

array = np.ndarray

profiles = ['car', 'foot', 'bicycle']


def generate_points(n: int, min_x=55.65, max_x=55.82, min_y=37.45, max_y=37.75) -> array:
    """Массив рандомных точек в квадрате."""
    diff_x, diff_y = max_x - min_x, max_y - min_y
    return np.random.random_sample((n, 2)) * np.array([diff_x, diff_y]) + np.array([min_x, min_y])


def generate_depot(depot_id: int, loc: Tuple[float, float], load=300):
    start = 10 + randint(-2, 2)
    end = 20 + randint(-2, 2)
    tw = (str_to_ts(f'2020-10-01T{start}:00:00Z'), str_to_ts(f'2020-10-01T{end}:00:00Z'))
    lat, lon = loc
    depot = Depot(
        id=depot_id,
        time_window=tw,
        lat=lat,
        lon=lon,
        delay=load,
        name=f'depot_{depot_id}',
    )
    return depot


def generate_window(i: int) -> Tuple[int, int]:
    return str_to_ts(f"2020-10-01T{10 + (i % 4)}:00:00Z"), str_to_ts(f"2020-10-01T{(12 + (i % 4))}:00:00Z")


def generate_job(job_id: int, point: Tuple[float, float], depot: Depot, val=2, delay=300) -> Job:
    return Job(
        id=job_id,
        name=f'job_{job_id}',
        lat=point[0],
        lon=point[1],
        delay=delay,
        time_windows=[generate_window(job_id)],
        capacity_constraints=[val, val],
        required_skills=[],
        priority=1,
        depots=[depot],
    )


def generate_jobs(points: List[Tuple[float, float]], depot: Depot, val=2, delay=300) -> List[Job]:
    return [generate_job(i, point, depot, val, delay) for i, point in enumerate(points)]


def generate_profile() -> str:
    return profiles[randint(0, 2)]


def generate_agent(profile: str, agent_id: int, depots: List[Depot], val=20) -> Agent:
    start = 10 + randint(-2, 2)
    end = 20 + randint(-2, 2)
    tw = [
        (
            str_to_ts(f'2020-10-01T{start}:00:00Z'),
            str_to_ts(f'2020-10-01T{end}:00:00Z'),
        )
    ]
    agent = Agent(
        id=agent_id,
        name=f'agent_{agent_id}',
        costs={"fixed": 22.0, "distance": 0.0002, "time": 0.004806},
        capacity_constraints=[val, val],
        time_windows=tw,
        compatible_depots=depots,
        profile=profile,
        skills=[],
    )
    return agent


def generate_vrp(jobs: int, agents: int) -> Tuple[List[Agent], List[Job], Depot]:
    size = jobs + 1
    pts = generate_points(size)
    points = to_list(pts)
    depot = generate_depot(0, points[0])
    jobs_list = generate_jobs(points[1:], depot)
    agents_list = [generate_agent(generate_profile(), i, [depot]) for i in range(agents)]
    return agents_list, jobs_list, depot


def generate_mdvrp(jobs: int, storages: int, agents: int) -> Tuple[List[Agent], List[Job], List[Depot]]:
    size = jobs * storages + storages
    pts = generate_points(size)
    points = to_list(pts)

    depots_list = [generate_depot(i, points[i]) for i in range(storages)]
    agents_list = [generate_agent(generate_profile(), i, depots_list) for i in range(agents)]
    jobs_list = []
    for storage_id in range(storages):
        for j in range(jobs):
            job_id = storages + storage_id * storages + j
            jobs_list.append(generate_job(job_id, points[job_id], depots_list[storage_id]))

    return agents_list, jobs_list, depots_list
