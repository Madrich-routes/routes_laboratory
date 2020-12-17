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

    # помещаем самый большой склад в конец
    big_depot = depots_list[6]
    depots_list.remove(big_depot)
    depots_list.append(big_depot)

    pts = [(depot.lat, depot.lon) for depot in depots_list]
    problem = RichMDVRPProblem(
        agents_list,
        get_problems(jobs_list, depots_list, profile_dict),
        PlaceMapping(places=depots_list, geometries=get_geometries(pts, profile_dict)),
    )
    solver = RustSolver()
    solution = solver.solve_mdvrp(problem)
    return export_to_excel(export(solution), settings.DATA_DIR / "eapteka_result_sorted.xlsx")


if __name__ == "__main__":
    run_eapteka()
