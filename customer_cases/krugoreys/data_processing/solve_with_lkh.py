from pathlib import Path
from typing import Tuple, List

import numpy as np

from models.graph.distance_matrix import DistanceMatrix
from models.problems.cvrptw import CVRPTWProblem
from models.rich_vrp.agent import Agent
from models.rich_vrp.job import Job
from solvers.external.lkh import LKHSolver
from solvers.transformational import TransformationalSolver
from transformers.clipper import remove_longer
from transformers.fake_depot import add_fake_depot
from transformers.scaler import MatrixScaler, scale_down
from utils.logs import logger
from utils.serialization import read_pickle, save_pickle

Point = Tuple[float, float]


def solve(
        matrix: DistanceMatrix,
        vehicles: List[Agent],
        tasks: List[Job],
):
    solver = TransformationalSolver(
        transformers=[],
        basic_solver=LKHSolver()
    )

    matrix = matrix.distance_matrix
    remove_longer(matrix, a_max=50 * 1000)  # оставляем только то, что < 50 км

    matrix = add_fake_depot(
        matrix,
        start_ids=np.array([int(v.start_place) for v in vehicles]),
        end_ids=np.array([int(v.end_place) for v in vehicles]),
    )

    matrix = scale_down(matrix, max_value=262144)

    start_time = min(t.tw_start for t in tasks)
    end_time = max(t.tw_start for t in tasks)

    problem = CVRPTWProblem(
        matrix=matrix,
        vehicles=len(vehicles),
        vehicles_capacity=10 ** 5,
        max_len=1000,
        max_hops=1000,
        demands=[0] + [1] * len(tasks),
        time_windows=[(start_time, end_time)] * (len(tasks) + 1)  # + [(int(t.tw_start), int(t.tw_end)) for t in tasks],
    )

    return solver.solve(problem)


# /tmp/solutions/solution_lkh-4892400.sol

def main():
    data_dir = Path('../big_data')

    logger.info('Загружаем данные...')
    tasks = read_pickle(data_dir / 'tasks.pkl.gz', compression='gzip')
    vehicles = read_pickle(data_dir / 'vehicles.pkl.gz', compression='gzip')
    matrix = read_pickle(data_dir / 'matrix_big.pkl.gz', compression='gzip')

    print('Решаем')
    res = solve(matrix=matrix, tasks=tasks, vehicles=vehicles)

    save_pickle(data_dir / 'solution.pkl', res)
    print(res)


if __name__ == "__main__":
    main()
