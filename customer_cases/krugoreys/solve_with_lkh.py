from pathlib import Path

from celery.worker.consumer import Tasks

from customer_cases.krugoreys.solving.models import DistanceMatrix, Vehicle
from models.problems.cvrptw import CVRPTWProblem
from solvers.external.lkh import LKHSolver
import numpy as np

from solvers.transformational import TransformationalSolver
from transformers.clipper import DistanceClipper

from dataclasses import dataclass
from typing import Tuple, List, Dict, Optional
import numpy as np

from utils.serialization import read_pickle, save_pickle

Point = Tuple[float, float]


def solve(
        matrix: DistanceMatrix,
        vehicles: List[Vehicle],
        tasks: List[Tasks],
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
        time_windows=[(int(t.start_time), int(t.end_time)) for t in tasks],
    )

    return solver.solve(problem)


def main():
    data_dir = Path('/media/dimitrius/avg_data/Krugoreys/big_data')

    matrix = read_pickle(data_dir / 'matrix.pkl.gz', compression='gzip')
    tasks = read_pickle(data_dir / 'tasks.pkl.gz', compression='gzip')
    vehicles = read_pickle(data_dir / 'vehicles.pkl.gz', compression='gzip')

    res = solve(matrix=matrix, tasks=tasks, vehicles=vehicles)

    save_pickle(data_dir / 'solution.pkl', res)
    print(res)


if __name__ == "__main__":
    main()
