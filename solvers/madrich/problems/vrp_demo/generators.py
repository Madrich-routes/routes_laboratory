from typing import List

import numpy as np

from madrich.api_module import fake_module
from madrich.problems.models import Window, Point, Cost, Matrix
from madrich.problems.vrp_demo.models import Storage, Job, Courier
from madrich.tests.generators import generate_points


def generate_storage(n: int, loc: Point, load=300):
    w = Window(("2020-10-01T10:00:00Z", "2020-10-01T20:00:00Z"))
    storage = Storage(f'storage_{n}', load, ['brains'], loc, w)
    return storage


def generate_jobs(points: List[Point], storage_id: str = '', val=2, delay=300) -> List[Job]:
    jobs = []
    for i, point in enumerate(points):
        job_id = f'{storage_id}_job_{i}'
        value = np.array([val, val])
        skills = ['brains']
        w = Window((f"2020-10-01T{10 + (i % 4)}:00:00Z", f"2020-10-01T{(12 + (i % 5))}:00:00Z"))
        tw = [w]
        jobs.append(Job(job_id, delay, value, skills, point, tw))
    return jobs


def generate_couriers(n: int, start: Point, end: Point, val=20) -> List[Courier]:
    couriers = []
    for i in range(n):
        name = f'courier_{i}'
        cost = Cost(10., 0.5, 1.2)
        value = np.array([val, val])
        skills = ['brains']
        max_distance = 100_000
        w = Window(("2020-10-01T10:00:00Z", "2020-10-01T20:00:00Z"))
        couriers.append(Courier(name, 'driver', cost, value, skills, max_distance, w, start, end))
    return couriers


def generate_vrp(points: int, storage_name=''):
    pts = generate_points(1 + points)
    distance, travel_time = fake_module.get_matrix(pts, ['distance', 'travelTime'])
    matrix = Matrix('driver', distance, travel_time)
    p_list = []
    for i in range(len(pts)):
        p_list.append(Point(i, (pts[i][0], pts[i][1])))
    storage = generate_storage(0, p_list[0])
    couriers = generate_couriers(5, p_list[0], p_list[0])
    jobs = generate_jobs(p_list[1:], storage.name if not storage_name else storage_name)
    return jobs, couriers, matrix, storage
