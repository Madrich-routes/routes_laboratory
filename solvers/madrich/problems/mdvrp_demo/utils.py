from typing import List

import matplotlib.pyplot as plt

from solvers.madrich.problems.mdvrp_demo.models import Storage, Tour
from solvers.madrich.utils import draw_points, draw_route


def draw_mdvrp(storages: List[Storage], tour: Tour):
    points_storages = []
    for storage in storages:
        points_storages.append(storage.location.point)
    assigned = []
    for storage in tour.storages:
        assigned += storage.assigned_jobs
    assigned = [job.location.point for job in assigned]
    unassigned = []
    for storage in tour.storages:
        unassigned += storage.unassigned_jobs
    unassigned = [job.location.point for job in unassigned]

    for route in tour.routes:
        draw_points(points_storages, 'r', False)
        draw_points(assigned, 'y', False)
        draw_points(unassigned, 'g', False)
        start = route.courier.start_location.point
        end = route.courier.end_location.point
        draw_points([start, end], 'c', False)

        points = [start]
        for track in route.tracks:
            points.append(track.storage.location.point)
            for job in track.jobs:
                points.append(job.location.point)
        points.append(end)
        t = [i for i in range(len(points))]
        draw_route(t, points, 'b', False)

        plt.show()
