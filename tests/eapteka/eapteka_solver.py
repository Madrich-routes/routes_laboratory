from functools import partial
import numpy as np
import settings
from customer_cases.eapteka.problem_formulation import (
    build_eapteka_problem,
    AptekaParams,
)
from datetime import datetime
from models.rich_vrp.geometries.geometry import HaversineGeometry
from models.rich_vrp.place_mapping import PlaceMapping
from customer_cases.eapteka.genetic_solver.eapteka_solver import EaptekaSolver

if __name__ == '__main__':

    problem_params = AptekaParams(
        delay_pharmacy=5 * 60,
        delay_stock=10 * 60,
        pedestrian_max_weight=15,
        pedestrian_max_volume=40,
        driver_max_weight=15,
        driver_max_volume=40,
        point_delay=5,
    )

    problem = build_eapteka_problem(
        data_folder=settings.DATA_DIR / "eapteka/data",
        params=problem_params,
        profile_geometries={
            "driver": partial(HaversineGeometry, default_speed=15),
            "pedestrian": partial(HaversineGeometry, default_speed=1.5),
        },
    )
    # сокращаем проблему для скорости решения
    # для теста оставим на каждый склад по n job'ов
    print(datetime.fromtimestamp(5))
    n = 10
    jobs_per_depot = [n for i in range(len(problem.depots))]
    jobs = []
    for job in problem.jobs:
        if jobs_per_depot[job.depots[0].id] > 0:
            jobs_per_depot[job.depots[0].id] -= 1
            jobs.append(job)
            if sum(jobs_per_depot) == 0:
                break

    problem.jobs = jobs
    places = list(problem.depots) + list(problem.jobs)
    points = np.array([[p.lat, p.lon] for p in places])

    profile_geometries = {
        "driver": partial(HaversineGeometry, default_speed=15),
        "pedestrian": partial(HaversineGeometry, default_speed=1.5),
    }
    geometries = {
        'driver': profile_geometries['driver'](points),
        'pedestrian': profile_geometries['pedestrian'](points),
    }
    problem.matrix = PlaceMapping(places=places, geometries=geometries)
    problem.agents = problem.agents[:5]
    meta_solver = EaptekaSolver(problem, "rust")
    solutions = meta_solver.solve()
    k = 0
