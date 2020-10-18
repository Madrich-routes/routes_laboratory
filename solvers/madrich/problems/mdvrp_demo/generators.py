from typing import List, Tuple, Dict

import numpy as np

from madrich.api_module import fake_module
from madrich.problems.mdvrp_demo.models import Storage, Job, Courier
from madrich.problems.models import Window, Point, Matrix, Cost
from madrich.tests.generators import generate_points


def generate_mdvrp(jobs: int, storages: int, couriers: int) -> Tuple[List[Storage], List[Courier], Dict[str, Matrix]]:
    pts = generate_points(jobs * storages + storages + 1, max_x=55.8, max_y=37.7, min_x=55.7, min_y=37.6)
    distance, travel_time = fake_module.get_matrix(pts, ['distance', 'travelTime'])
    matrix = Matrix('driver', distance, travel_time)

    points_list = []
    for i in range(len(pts)):
        points_list.append(Point(i, (pts[i][0], pts[i][1])))

    storages_list = []
    for i in range(storages):
        storage_id = f'storage_{i}'
        storages_list.append(Storage(
            name=f'storage_{i}',
            load=300,
            skills=['brains'],
            location=points_list[jobs * storages + i],
            work_time=Window(("2020-10-01T10:00:00Z", "2020-10-01T20:00:00Z")),
            unassigned_jobs=generate_jobs(points_list[i * jobs: (i + 1) * jobs], storage_id),
            assigned_jobs=[]
        ))

    couriers_list = []
    for i in range(couriers):
        start = end = points_list[-1]
        name = f'courier_{i}'
        cost = Cost(10., 0.5, 1.2)
        value = np.array([40, 80])
        skills = ['brains']
        max_distance = 1_000_000
        w = Window(("2020-10-01T10:00:00Z", "2020-10-01T20:00:00Z"))
        couriers_list.append(Courier(name, 'driver', cost, value, skills, max_distance, w, start, end, storages_list))

    return storages_list, couriers_list, {'driver': matrix}


def generate_jobs(points: List[Point], storage_id: str = '', delay=300) -> List[Job]:
    jobs = []

    for i, point in enumerate(points):
        job_id = f'{storage_id}_job_{i}'
        value = np.array([1, 2])
        skills = ['brains']
        w = Window((f"2020-10-01T{10 + (i % 4)}:00:00Z", f"2020-10-01T{(12 + (i % 5))}:00:00Z"))
        tw = [w]
        jobs.append(Job(job_id, delay, value, skills, point, tw))

    return jobs
