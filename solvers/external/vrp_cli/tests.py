from solvers.external.vrp_cli.generators import generate_vrp
from solvers.external.vrp_cli.solver import RustSolver


def test_run_solver():
    """ Тест на запуск первого слоя - слоя запуска солвера """
    problem = generate_vrp(20, 4)
    solver = RustSolver()
    solver.solve(problem)


if __name__ == "__main__":
    test_run_solver()
