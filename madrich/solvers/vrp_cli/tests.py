from typing import List

import numpy as np
import ujson

from madrich.formats.export import export
from madrich.models.rich_vrp.depot import Depot
from madrich.models.rich_vrp.job import Job
from madrich.models.rich_vrp.place_mapping import PlaceMapping
from madrich.models.rich_vrp.problem import RichVRPProblem, RichMDVRPProblem
from madrich.solvers.vrp_cli.builders import get_geometries
from madrich.solvers.vrp_cli.generators import generate_mdvrp, generate_vrp
from madrich.solvers.vrp_cli.solver import RustSolver

geom_profiles = {"car": ("car", np.nan), "foot": ("foot", np.nan), "bicycle": ("bicycle", np.nan)}


def get_problems(jobs_list: List[Job], depots_list: List[Depot]) -> List[RichVRPProblem]:
    problems = []

    for depot in depots_list:
        this_depot_jobs = [job for job in jobs_list if job.depot.id == depot.id]

        pts = [(job.lat, job.lon) for job in this_depot_jobs] + [(depot.lat, depot.lon)]
        geometries = get_geometries(pts, geom_profiles)
        places = [depot] + this_depot_jobs  # noqa
        problem = RichVRPProblem(
            place_mapping=PlaceMapping(places=places, geometries=geometries),
            agents=[],
            jobs=this_depot_jobs,
            depot=depot,
        )
        problems.append(problem)

    return problems


def test_vrp_solver():
    """ Тест на запуск первого слоя - слоя запуска солвера """
    agents_list, jobs_list, depot = generate_vrp(20, 4)
    pts = [(job.lat, job.lon) for job in jobs_list] + [(depot.lat, depot.lon)]
    geometries = get_geometries(pts, geom_profiles)

    places = [depot] + jobs_list  # noqa
    problem = RichVRPProblem(
        place_mapping=PlaceMapping(places=places, geometries=geometries),
        agents=agents_list,
        jobs=jobs_list,
        depot=depot,
    )
    solver = RustSolver()
    solver.solve(problem)


def test_mdvrp_solver():
    """ Тест на запуск второго слоя - слоя решения задачи с несколькими складами """
    agents_list, jobs_list, depots_list = generate_mdvrp(20, 4, 10)
    pts = [(depot.lat, depot.lon) for depot in depots_list]
    problem = RichMDVRPProblem(
        agents_list,
        get_problems(jobs_list, depots_list),
        PlaceMapping(places=depots_list, geometries=get_geometries(pts, geom_profiles)),
    )
    solver = RustSolver()
    solution = solver.solve_mdvrp(problem)
    data = export(solution)
    print(ujson.dumps(data))


def test_times():
    """
    А правильно ли у нас считается время в солвере?
    """
    agents_list, jobs_list, depots_list = generate_mdvrp(15, 3, 2)
    pts = [(depot.lat, depot.lon) for depot in depots_list]
    problem = RichMDVRPProblem(
        agents_list,
        get_problems(jobs_list, depots_list),
        PlaceMapping(places=depots_list, geometries=get_geometries(pts, geom_profiles)),
    )
    solver = RustSolver()
    solution = solver.solve_mdvrp(problem)
    error = 0
    for i, routes in solution.routes.items():
        for route in routes:
            depot = route.waypoints[0].place
            problem = next((p for p in solution.problem.sub_problems if p.depot == depot), None)
            for j in range(1, len(route.waypoints)):
                time_by_matrix = int(
                    problem.matrix.time(route.waypoints[j - 1].place, route.waypoints[j].place, route.agent.profile)
                )
                time_by_solver = route.waypoints[j].arrival - route.waypoints[j - 1].departure
                if time_by_matrix != time_by_solver:
                    error += abs(time_by_matrix - time_by_solver)

    print(error)


test_mdvrp_solver()
