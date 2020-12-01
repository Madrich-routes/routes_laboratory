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
from madrich.solvers.vrp_cli.builders import get_geometries

from madrich.geo.providers import osrm_module

geom_profiles = {"car": ("car", np.nan), "foot": ("foot", np.nan), "bicycle": ("bicycle", np.nan)}


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
    agents_list, jobs_list, depots_list = generate_mdvrp(15, 3, 2)
    pts = [(depot.lat, depot.lon) for depot in depots_list]
    problem = RichMDVRPProblem(
        agents_list,
        get_problems(jobs_list, depots_list),
        PlaceMapping(places=depots_list, geometries=get_geometries(pts, geom_profiles)),
    )
    solver = RustSolver()
    solution = solver.solve_mdvrp(problem)
    print(export(solution))


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
            for i in range(1, len(route.waypoints)):
                time_by_matrix = int(
                    problem.matrix.time(route.waypoints[i - 1].place, route.waypoints[i].place, route.agent.profile)
                )
                time_by_solver = route.waypoints[i].arrival - route.waypoints[i - 1].departure
                if time_by_matrix != time_by_solver:
                    error += abs(time_by_matrix - time_by_solver)

    print(error)


if __name__ == "__main__":
    test_mdvrp_solver()
    # path_to_excel = generate_random("test_problem.xlsx")
    # result = run_solver(settings.DATA_DIR / "eapteka.xls")
    # points = generate_points(20)
    # foot_matrix = get_matrix(points=points, factor="duration", transport="foot")
    # geom = TransportMatrixGeometry(points, foot_matrix)
    # time_matrix = geom.time_matrix()

    # test_times()

    # points = generate_points(20)
    # # car_matrix = get_matrix(points=points, factor="duration", transport="car")
    # dima_matrix, _ = osrm_module.get_osrm_matrix(
    #     src=points,
    #     transport="car",
    #     return_durations=False,
    # )

    # for i in range(len(points)):
    #     for j in range(len(points)):
    #         if i != j:
    #             print(f"Distance between {points[i]} and {points[j]} = {dima_matrix[i][j]/1000}")
