from datetime import datetime
from random import randint
from typing import List, Tuple, Set

import numpy as np

from models.rich_vrp.agent import Agent
from models.rich_vrp.depot import Depot
from models.rich_vrp.job import Job
from models.rich_vrp.place_mapping import PlaceMapping
from models.rich_vrp.problem import RichVRPProblem
from solvers.madrich.api_module.osrm_module import get_matrix

array = np.ndarray


def convert_from_str(t: str) -> int:
    return int(datetime.strptime(t, '%Y-%m-%dT%H:%M:%SZ').timestamp())


def to_list(points: array) -> List[Tuple[float, float]]:
    """array n * 2 to List[Point], Point = float, float
    :param points: points in ndarray format
    :return: points in list format
    """
    temp = []
    for point in points:
        temp.append((point[0], point[1]))
    return temp


def generate_points(
    n: int, min_x=55.65, max_x=55.82, min_y=37.45, max_y=37.75
) -> array:
    """Массив рандомных точек в квадрате."""
    diff_x, diff_y = max_x - min_x, max_y - min_y
    return np.random.random_sample((n, 2)) * np.array([diff_x, diff_y]) + np.array(
        [min_x, min_y]
    )


def generate_depot(depot_id: int, loc: Tuple[float, float], load=300):
    start = 10  # + randint(-2, 2)
    end = 20  # + randint(-2, 2)
    tw = [
        (
            convert_from_str(f'2020-10-01T{start}:00:00Z'),
            convert_from_str(f'2020-10-01T{end}:00:00Z'),
        )
    ]
    lat, lon = loc
    depot = Depot(
        id=depot_id,
        time_windows=tw,
        lat=lat,
        lon=lon,
        delay=load,
        name=f'depot_{depot_id}',
    )
    return depot


def generate_window(i: int) -> Tuple[int, int]:
    return convert_from_str(f"2020-10-01T{10 + (i % 4)}:00:00Z"), convert_from_str(
        f"2020-10-01T{(12 + (i % 4))}:00:00Z"
    )


def generate_jobs(
    points: List[Tuple[float, float]], depot: Depot, val=2, delay=300
) -> List[Job]:
    jobs = [
        Job(
            id=i,
            name=f'job_{i}',
            lat=point[0],
            lon=point[1],
            delay=delay,
            time_windows=[generate_window(i)],
            capacity_constraints=[val, val],
            required_skills=[],
            priority=1,
            depots=[depot],
        )
        for i, point in enumerate(points)
    ]
    return jobs


def generate_profile() -> str:
    profile = randint(0, 2)
    if profile == 0:
        return 'bicycle'
    elif profile == 1:
        return 'pedestrian'
    else:
        return 'driver'


def generate_agent(profile: str, agent_id: int, depots: List[Depot], val=20) -> Agent:
    start = 10  # + randint(-2, 2)
    end = 20  # + randint(-2, 2)
    tw = [
        (
            convert_from_str(f'2020-10-01T{start}:00:00Z'),
            convert_from_str(f'2020-10-01T{end}:00:00Z'),
        )
    ]
    agent = Agent(
        id=agent_id,
        name=f'agent_{agent_id}',
        costs={"fixed": 22.0, "distance": 0.0002, "time": 0.004806},
        capacity_constraints=[val, val],
        time_windows=tw,
        compatible_depots=set(depots),
        start_place=depots[0],
        end_place=depots[0],
        profile=profile,
        skills=[],
    )
    return agent


def generate_vrp(jobs: int, agents: int) -> RichVRPProblem:
    size = jobs + 1
    pts = generate_points(size)
    points = to_list(pts)
    depot = generate_depot(0, points[0])
    jobs_list = generate_jobs(points[1:], depot)
    agents_list = []
    for i in range(agents):
        agents_list.append(generate_agent(generate_profile(), i, [depot]))

    geometries = {
        "driver": {
            "dist_matrix": get_matrix(points=pts, factor='distance', transport='car'),
            "time_matrix": get_matrix(points=pts, factor='duration', transport='car'),
        },
        "pedestrian": {
            "dist_matrix": get_matrix(points=pts, factor='distance', transport='foot'),
            "time_matrix": get_matrix(points=pts, factor='duration', transport='foot'),
        },
        "bicycle": {
            "dist_matrix": get_matrix(
                points=pts, factor='distance', transport='bicycle'
            ),
            "time_matrix": get_matrix(
                points=pts, factor='duration', transport='bicycle'
            ),
        },
    }
    places = [depot] + jobs_list
    return RichVRPProblem(
        place_mapping=PlaceMapping(places=places, geometries=geometries),
        agents=agents_list,
        jobs=jobs_list,
        depot=depot,
    )


if __name__ == '__main__':
    # print(get_matrix(generate_points(15), 'distance', 'car'))
    problem = generate_vrp(15, 3)
    i = 0
