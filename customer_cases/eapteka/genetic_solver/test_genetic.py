from typing import Tuple

import numpy as np
from madrich.api_module.fake_module import get_matrix
from madrich.tests.generators import generate_points
from madrich.utils import to_list

from customer_cases.eapteka.genetic_solver.models import Task, Depot, Courier
from customer_cases.eapteka.genetic_solver.runner import runner

array = np.ndarray
Point = Tuple[float, float]


def generate_task():
    points = to_list(generate_points(20))
    depot_loc = to_list(generate_points(1))[0]
    start_loc, end_loc = (55.745763, 37.604962), (55.751038, 37.600797)
    mapping = {}

    i = 0
    for point in points:
        mapping[point] = i
        i += 1
    mapping[depot_loc] = i
    mapping[start_loc], mapping[end_loc] = i + 1, i + 2
    points += [depot_loc, start_loc, end_loc]

    distance = {'driver': get_matrix(points), 'pedestrian': get_matrix(points)}
    travel_time = {'driver': get_matrix(points), 'pedestrian': get_matrix(points)}

    size = len(points)
    times = [(f"2020-10-01T{10 + (i % 4) * 2}:00:00Z", f"2020-10-01T{(12 + (i % 4) * 2)}:00:00Z") for i in range(size)]

    tasks = [Task(mapping[points[i]], [times[i]], 1., [2, 2], 1) for i in range(size)]
    depot = Depot('storage', mapping[depot_loc], 1., 1.)

    couriers = [
        Courier('pedestrian_1', 'pedestrian', 'Dmitriy',
                {"time": 0., "distance": 0., "fixed": 10},
                [(f"2020-10-01T10:00:00Z", f"2020-10-01T18:00:00Z")], 1, [10, 10],
                mapping[start_loc], mapping[end_loc]),
        Courier('driver_1', 'driver', 'Vladimir',
                {"time": 0., "distance": 0., "fixed": 10},
                [(f"2020-10-01T10:00:00Z", f"2020-10-01T18:00:00Z")], 1, [20, 20],
                mapping[start_loc], mapping[end_loc])
    ]

    return tasks, depot, couriers, ['driver', 'pedestrian'], distance, travel_time


def one_solver():
    tasks, depot, couriers, profiles, distance, travel_time = generate_task()
    runner(tasks, depot, couriers, profiles, distance, travel_time)


one_solver()
