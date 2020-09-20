from dataclasses import dataclass

import numpy as np
import os
import subprocess

import tsplib95

import settings
from formats.tsplib import dumps_matrix
from models.problems.base import BaseRoutingProblem, LKHSolvable
from solvers.transformational import BaseTransformationalSolver
from transformers.scaler import MatrixScaler


class LKHSolver(BaseTransformationalSolver):
    def __init__(
            self,
            tsp_path: str = settings.PROBLEM_FILE,
            par_path: str = settings.LKH_PAR_FILE,
            res_path: str = settings.VRP_RES_FILE,
            solver_path: str = settings.LKH3_PATH,
            trace_level: int = 1,
            runs: int = 10,
            max_trials: int = 2392,  # дефолтные значения нужно перепроверить
            max_swaps: int = 2392,
    ):
        """
        Trace level может быть от 1 до 3
        MAX_CANDIDATES = 4
        MAX_SWAPS = 400
        MAX_TRIALS = 1000
        KICKS = 0
        RUNS = 2
        """
        super().__init__(
            transformers=[
                # MatrixScaler(max_value=262144)
            ]
        )
        self.problem: LKHSolvable = None

        # TODO: к этим парням нужно приделать pid и хеши,
        #  чтобы никто ни с кем не пересекся когда много потоков и тд
        self.tsp_path: str = tsp_path
        self.par_path: str = par_path
        self.res_path: str = res_path

        self.solver_path: str = solver_path
        self.trace_level: int = trace_level

    def basic_solve(self, p: BaseRoutingProblem):
        self.problem = p
        self.dump_problem()
        return self.run_solver()

        # TODO: преобразовать к решению

    def split_into_tours(self, nodes, size):
        """
        TODO: Осознать и написать коммент
        """
        nodes *= nodes < size

        bounds = np.where(nodes == 0)[0]
        res = [nodes[bounds[-1]:]]
        for i in range(len(bounds) - 1):
            res += [nodes[bounds[i]: bounds[i + 1] + 1]]

        return res

    def run_solver(self):
        print('Вызываем солвер...')
        output = subprocess.check_output([self.solver_path, self.par_path], shell=False)
        return self.parse_solution(), output

    def parse_solution(self):
        """
        Парсим файл решения
        """
        solution = tsplib95.load_solution(self.res_path)
        return np.array(solution.tours[0])

    def solver_par(self) -> str:
        """
        Часть файла параметров, которая относится к конфигурации солвера
        """
        return '\n'.join([
            f"PROBLEM_FILE = {self.tsp_path}",
            f"TOUR_FILE = {self.res_path}",
            f"TRACE_LEVEL = {self.trace_level}",
        ])

    def dumps_params(self) -> str:
        """
        Итоговая строка параметров с учетом параметров проболемы.
        """
        return self.solver_par() + self.problem.lkh_par()

    def dumps_problem(self) -> str:
        """
        Получаем строку с tsplib описание проблемы
        """
        return self.problem.lkh_problem()

    def dump_problem(self) -> None:
        with open(self.par_path, "w") as dest:
            dest.write(self.dumps_params())

        with open(self.tsp_path, "w") as dest:
            dest.write(self.dumps_problem())
