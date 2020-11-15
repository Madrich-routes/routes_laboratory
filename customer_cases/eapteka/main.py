import faulthandler
import logging
from functools import partial

import settings
from customer_cases.eapteka.problem_formulation import build_eapteka_problem, AptekaParams
from formats import api
from models.rich_vrp.geometries.geometry import HaversineGeometry
from solvers.external.vrp_cli.solver import RustSolver


if __name__ == "__main__":
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
        data_folder=settings.DATA_DIR / 'eapteka/data',
        params=problem_params,
        profile_geometries={
            'driver': partial(HaversineGeometry, default_speed=15),
            'pedestrian': partial(HaversineGeometry, default_speed=1.5),
        }
    )

    solver = RustSolver()
    solution = solver.solve(problem)
    solution_str = api.export(solution)

    print(solution_str)
