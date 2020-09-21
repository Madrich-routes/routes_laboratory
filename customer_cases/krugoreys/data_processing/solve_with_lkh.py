from pathlib import Path
from typing import Tuple, List

from customer_cases.krugoreys.solving.models import DistanceMatrix, Vehicle, Task
from models.problems.cvrptw import CVRPTWProblem
from solvers.external.lkh import LKHSolver
from solvers.transformational import TransformationalSolver
from transformers.clipper import DistanceClipper
from utils.serialization import read_pickle, save_pickle

Point = Tuple[float, float]


def solve(
        matrix: DistanceMatrix,
        vehicles: List[Vehicle],
        tasks: List[Task],
):
    solver = TransformationalSolver(
        transformers=[
            DistanceClipper(
                a_min=12 * 3600,
                a_max=24 * 3600,
            )
        ],
        basic_solver=LKHSolver()
    )

    problem = CVRPTWProblem(
        matrix=matrix.time_matrix,
        vehicles=len(vehicles),
        vehicles_capacity=10 ** 5,
        max_len=1000,
        max_hops=1000,
        demands=[1] * len(tasks),
        time_windows=[(int(t.tw_start), int(t.tw_end)) for t in tasks],
    )

    return solver.solve(problem)


def main():
    data_dir = Path('../big_data')

    print('Загружаем данные')
    tasks = read_pickle(data_dir / 'tasks.pkl.gz', compression='gzip')
    vehicles = read_pickle(data_dir / 'vehicles.pkl.gz', compression='gzip')
    matrix = read_pickle(data_dir / 'matrix.pkl.gz', compression='gzip')

    print('Решаем')
    res = solve(matrix=matrix, tasks=tasks, vehicles=vehicles)

    save_pickle(data_dir / 'solution.pkl', res)
    print(res)


if __name__ == "__main__":
    main()
