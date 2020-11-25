import os
from pathlib import Path

from madrich.config import settings
from madrich.formats.excel.universal import StandardDataFormat
from madrich.formats.export import export
from madrich.models.rich_vrp.place_mapping import PlaceMapping
from madrich.models.rich_vrp.problem import RichMDVRPProblem
from madrich.solvers.vrp_cli.generators import generate_mdvrp
from madrich.solvers.vrp_cli.solver import RustSolver
from madrich.solvers.vrp_cli.tests import get_problems, get_geometry


def run_solver(filename: str) -> dict:
    file = settings.UPLOAD_DIR / filename
    agents_list, jobs_list, depots_list, profile_list = StandardDataFormat.from_excel(file)
    pts = [(depot.lat, depot.lon) for depot in depots_list]
    problem = RichMDVRPProblem(
        agents_list,
        get_problems(jobs_list, depots_list),
        PlaceMapping(places=depots_list, geometries=get_geometry(pts)),
    )
    solver = RustSolver()
    solution = solver.solve_mdvrp(problem)
    return export(solution)


def generate_random(filename: str) -> Path:
    file = settings.UPLOAD_DIR / filename
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    agents, jobs, depots = generate_mdvrp(20, 4, 10)
    StandardDataFormat.to_excel(agents, jobs, depots, file)
    return file
