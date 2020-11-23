from solvers.external.vrp_cli.generators import generate_vrp
from solvers.external.vrp_cli.solver import RustSolver


def run_solver():
    problem = generate_vrp(20, 4)
    solver = RustSolver()
    solution = solver.solve(problem)


if __name__ == "__main__":
    run_solver()
