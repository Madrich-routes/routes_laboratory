import os
from pathlib import Path

from madrich.config import settings
from madrich.formats.excel.universal import StandardDataFormat
from madrich.formats.export import export
from madrich.models.rich_vrp.place_mapping import PlaceMapping
from madrich.models.rich_vrp.problem import RichMDVRPProblem
from madrich.solvers.vrp_cli.generators import generate_mdvrp
from madrich.solvers.vrp_cli.solver import RustSolver
from madrich.solvers.vrp_cli.builders import get_geometries, get_problems


def run_solver(filename: str) -> dict:
    """
    Получаем нашу эксельку с данными, из нее генерируем проблемy,
    проблему передаем солверу, получаем результат и возвращаем в формате API.

    Parameters
    ----------
    filename: Имя эксельки с данными

    Returns
    ----------
    dict с ответом в формате API
    """
    file = settings.UPLOAD_DIR / filename
    agents_list, jobs_list, depots_list, profile_dict = StandardDataFormat.from_excel(file)
    pts = [(depot.lat, depot.lon) for depot in depots_list]
    problem = RichMDVRPProblem(
        agents_list,
        get_problems(jobs_list, depots_list, profile_dict),
        PlaceMapping(places=depots_list, geometries=get_geometries(pts, profile_dict)),
    )
    solver = RustSolver()
    solution = solver.solve_mdvrp(problem)
    return export(solution)


def generate_random(filename: str) -> Path:
    """
    Генерируем случайную задачу и сохраняем в нашу эксельку
    filename: Имя будущей эксельки

    Returns
    ----------
    Path на сгенерированный файл
    """
    file = settings.UPLOAD_DIR / filename
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    agents, jobs, depots = generate_mdvrp(20, 4, 10)
    StandardDataFormat.to_excel(agents, jobs, depots, file)
    return file
