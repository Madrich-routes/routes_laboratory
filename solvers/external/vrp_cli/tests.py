from models.rich_vrp.place_mapping import PlaceMapping
from models.rich_vrp.problem import RichVRPProblem
from solvers.external.vrp_cli.generators import generate_vrp, profiles, generate_mdvrp
from solvers.external.vrp_cli.solver import RustSolver
from solvers.madrich.api_module.osrm_module import get_matrix


def get_geometry(pts) -> dict:
    geometries = {
        profile:
            {
                "dist_matrix": get_matrix(points=pts, factor='distance', transport=profile),
                "time_matrix": get_matrix(points=pts, factor='duration', transport=profile)
            }
        for profile in profiles
    }
    return geometries


def test_vrp_solver():
    """ Тест на запуск первого слоя - слоя запуска солвера """
    agents_list, jobs_list, depot = generate_vrp(20, 4)
    pts = [(job.lat, job.lon) for job in jobs_list] + [(depot.lat, depot.lon)]
    geometries = get_geometry(pts)

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
    pts = [(job.lat, job.lon) for job in jobs_list] + \
          [(depot.lat, depot.lon) for depot in depots_list]
    geometries = get_geometry(pts)


if __name__ == "__main__":
    test_vrp_solver()
