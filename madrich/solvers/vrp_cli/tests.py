from madrich.geo import transport
from typing import List

import numpy as np

from madrich.formats.export import export
from madrich.models.rich_vrp.depot import Depot
from madrich.models.rich_vrp.geometries.geometry import HaversineGeometry
from madrich.models.rich_vrp.job import Job
from madrich.models.rich_vrp.place_mapping import PlaceMapping
from madrich.models.rich_vrp.problem import RichVRPProblem, RichMDVRPProblem
from madrich.solvers.madrich.api_module.osrm_module import get_matrix
from madrich.solvers.vrp_cli.generators import generate_mdvrp, generate_vrp, profiles, generate_points
from madrich.solvers.vrp_cli.solver import RustSolver
from madrich.api.app.solver import run_solver, generate_random
from madrich.models.rich_vrp.geometries.transport import TransportMatrixGeometry

from madrich.config import settings
from madrich.geo.providers import osrm_module


def get_haversine_matrix(points: np.ndarray, factor: str, transport: str) -> np.ndarray:
    if transport == "driver":
        speed = 15
    elif transport == "bicycle":
        speed = 5
    else:
        speed = 1.5
    geom = HaversineGeometry(points, default_speed=speed)
    if factor == "distance":
        res = geom.dist_matrix()
    else:
        res = geom.time_matrix()
    return res


def get_haversine_geometry(pts) -> dict:
    geometries = {
        profile: {
            "dist_matrix": get_haversine_matrix(points=pts, factor="distance", transport=profile),
            "time_matrix": get_haversine_matrix(points=pts, factor="duration", transport=profile),
        }
        for profile in profiles
    }
    return geometries


def get_geometry(pts) -> dict:
    geometries = {
        profile: {
            "dist_matrix": get_matrix(points=pts, factor="distance", transport=profile),
            "time_matrix": get_matrix(points=pts, factor="duration", transport=profile),
        }
        for profile in profiles
    }
    return geometries


def get_problems(jobs_list: List[Job], depots_list: List[Depot]) -> List[RichVRPProblem]:
    problems = []

    for depot in depots_list:
        this_depot_jobs = [job for job in jobs_list if job.depot.id == depot.id]

        pts = [(job.lat, job.lon) for job in this_depot_jobs] + [(depot.lat, depot.lon)]
        geometries = get_haversine_geometry(pts)
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
    geometries = get_haversine_geometry(pts)

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
    agents_list, jobs_list, depots_list = generate_mdvrp(15, 3, 5)
    pts = [(depot.lat, depot.lon) for depot in depots_list]
    problem = RichMDVRPProblem(
        agents_list,
        get_problems(jobs_list, depots_list),
        PlaceMapping(places=depots_list, geometries=get_haversine_geometry(pts)),
    )
    solver = RustSolver()
    solution = solver.solve_mdvrp(problem)
    export(solution)


if __name__ == "__main__":
    # test_mdvrp_solver()
    # path_to_excel = generate_random("test_problem.xlsx")
    result = run_solver(settings.DATA_DIR / "eapteka.xls")
    # points = generate_points(20)
    # foot_matrix = get_matrix(points=points, factor="duration", transport="foot")
    # geom = TransportMatrixGeometry(points, foot_matrix)
    # time_matrix = geom.time_matrix()
