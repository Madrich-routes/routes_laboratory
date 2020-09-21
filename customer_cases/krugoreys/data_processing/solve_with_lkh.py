from pathlib import Path
from typing import Tuple, List

from statsmodels.iolib import load_pickle

from models.graph.distance_matrix import DistanceMatrix
from models.problems.cvrptw import CVRPTWProblem
from models.rich_vrp.agent import Agent
from models.rich_vrp.job import Job
from solvers.external.lkh import LKHSolver
from solvers.transformational import TransformationalSolver
from transformers.clipper import DistanceClipper
from transformers.fake_depot import add_fake_depot
from utils.logs import logger
from utils.serialization import read_pickle, save_pickle, load_np

import numpy as np

Point = Tuple[float, float]


def solve(
        matrix: DistanceMatrix,
        vehicles: List[Agent],
        tasks: List[Job],
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

    matrix = add_fake_depot(
        matrix.time_matrix,
        start_ids=np.array(v.start_place for v in vehicles),
        end_ids=np.array(v.end_place for v in vehicles),
    )

    problem = CVRPTWProblem(
        matrix=matrix.time_matrix,
        vehicles=len(vehicles),
        vehicles_capacity=10 ** 5,
        max_len=1000,
        max_hops=1000,
        demands=[0] + [1] * len(tasks),
        time_windows=[(int(t.tw_start), int(t.tw_end)) for t in tasks],
    )

    return solver.solve(problem)


def main():
    data_dir = Path('../big_data')

    logger.info('Загружаем данные...')
    tasks = read_pickle(data_dir / 'tasks.pkl.gz', compression='gzip')
    vehicles = read_pickle(data_dir / 'vehicles.pkl.gz', compression='gzip')
    matrix = load_pickle(data_dir / 'matrix_big.pkl.gz')

    print('Решаем')
    res = solve(matrix=matrix, tasks=tasks, vehicles=vehicles)

    save_pickle(data_dir / 'solution.pkl', res)
    print(res)


if __name__ == "__main__":
    main()
