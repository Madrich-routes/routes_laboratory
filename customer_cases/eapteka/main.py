import faulthandler
import logging

import settings
from customer_cases.eapteka import run
from customer_cases.eapteka.problem_formulation import build_eapteka_problem
# from solvers.external.vr
from formats import api
from solvers.external.vrp_cli.solver import RustSolver

faulthandler.enable()
logging.basicConfig(format='%(message)s', level=logging.INFO)

# TYPE = 'pedestrian'
# TYPE = 'bicycle'
# TYPE = 'transport_simple'
# TYPE = 'transport_complex'

# run.run_pharmacy(
#     type_m=TYPE,
#     time_pharmacy=5,
#     time_depot=10,
#     type_weight=15,
#     type_capacity=40,
#     driver_weight=200,
#     driver_capacity=400,
#     delay=5,
#     fg=TYPE + "_1_bet",  # номер результата
# )
#
# def main():
#     ...
#
# if __name__ == "__main__":
#     main()


if __name__ == "__main__":
    problem = build_eapteka_problem(settings.DATA_DIR / 'eapteka/data')
    solver = RustSolver()
    solution = solver.solve(problem)
    solution_str = api.export(solution)
