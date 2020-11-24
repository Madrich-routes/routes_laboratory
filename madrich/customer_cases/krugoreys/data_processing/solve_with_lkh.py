from pathlib import Path
from typing import List

import numpy as np
from transformers.clipper import make_symmetric, remove_longer
from transformers.fake_depot import add_fake_depot
from transformers.scaler import scale_down

from madrich.models import Geometry
from madrich.models.problems.mtsp import MTSPProblem
from madrich.models.rich_vrp import Agent
from madrich.models.rich_vrp.job import Job
from madrich.solvers.external.lkh import LKHSolver
from madrich.utils.logs import logger
from madrich.utils import read_pickle, save_pickle


def solve(
        matrix: Geometry,
        vehicles: List[Agent],
        tasks: List[Job],
):
    solver = LKHSolver(
        max_trials=150,
        runs=3,
        special=False,
        initial_tour='MTSP',
    )

    matrix = matrix.d  # берем за основу матрицу расстояний
    make_symmetric(matrix)  # делаем ее симетричной
    remove_longer(matrix, a_max=80 * 1000)  # оставляем только ребра < 80 км

    # задаем точки, где можно начинать и заканчивать
    matrix = add_fake_depot(
        matrix,
        start_ids=np.arange(len(matrix)),
        end_ids=np.arange(len(matrix)),
    )

    # скейлим, чтобы решалось LKH
    matrix = scale_down(matrix, max_value=536870912)

    problem = MTSPProblem(
        matrix=matrix,
        vehicles=len(vehicles),
        depot=1,
        objective='MINSUM',
        max_size=1000,
        min_size=1,
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
