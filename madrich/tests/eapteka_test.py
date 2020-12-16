from madrich.config import settings
from madrich.formats.excel.universal import StandardDataFormat
from madrich.formats.export import export, export_to_excel
from madrich.models.rich_vrp.place_mapping import PlaceMapping
from madrich.models.rich_vrp.problem import RichMDVRPProblem
from madrich.solvers.vrp_cli.builders import get_geometries, get_problems
from madrich.solvers.vrp_cli.solver import RustSolver


def run_eapteka():
    file = settings.DATA_DIR / "eapteka.xlsx"
    agents_list, jobs_list, depots_list, profile_dict = StandardDataFormat.from_excel(file)

    # для локального запуска
    # jobs_per_depot = 50
    # agents_list = agents_list[: len(depots_list)]
    # jobs_in_depot_counts = [jobs_per_depot for i in range(len(depots_list))]
    # jobs = []
    # for job in jobs_list:
    #     if jobs_in_depot_counts[job.depot.id] > 0:
    #         jobs_in_depot_counts[job.depot.id] -= 1
    #         jobs.append(job)
    # jobs_list = jobs

    pts = [(depot.lat, depot.lon) for depot in depots_list]
    problem = RichMDVRPProblem(
        agents_list,
        get_problems(jobs_list, depots_list, profile_dict),
        PlaceMapping(places=depots_list, geometries=get_geometries(pts, profile_dict)),
    )
    solver = RustSolver()
    solution = solver.solve_mdvrp(problem)
    return export_to_excel(export(solution), settings.DATA_DIR / "eapteka_result.xlsx")


if __name__ == "__main__":
    run_eapteka()
