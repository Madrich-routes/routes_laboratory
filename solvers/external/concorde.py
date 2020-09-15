import os
import subprocess

import tsplib95

import settings
from models.problems.base import BaseRoutingProblem
from models.problems.tsp import TSPProblem
from settings import PROBLEM_FILE
import numpy as np

from formats.tsplib import dumps_matrix
from solvers.transformational import BaseTransformationalSolver
from transformers.scaler import MatrixScaler


class ConcordeSolver(BaseTransformationalSolver):
    def __init__(
            self,
            problem: TSPProblem,
            tsp_path: str = settings.PROBLEM_FILE,
            par_path: str = settings.LKH_PAR_FILE,
            res_path: str = settings.VRP_RES_FILE,
            solver_path: str = settings.CONCORDE_PATH,  # бинарник concorde
            trace_level: int = 1,  # 1-3 по нарастанию словоблудия
    ):
        super().__init__()  # TODO: параметры!
        self.problem: BaseRoutingProblem = problem

        # TODO: к этим парням нужно приделать pid и хеши,
        #  чтобы никто ни с кем не пересекся когда много потоков и тд
        self.tsp_path: str = tsp_path
        self.par_path: str = par_path
        self.res_path: str = res_path

        self.solver_path: str = solver_path  # бинарник concorde
        self.trace_level: int = trace_level  # 1-3 по нарастанию словоблудия
        self.transformers = [
            MatrixScaler(max_value=32767)
        ]

    # TODO: привести все в порядок по интерфейсу
    def basic_solve(self):
        """
        Собственно получить решение из солвера
        """
        cur_dir = os.curdir
        os.chdir("/tmp/")

        output = subprocess.check_output([self.solver_path, self.tsp_path], shell=False)  # запускаем
        output = str(output).strip()  # очищаем output от мусора

        with open(self.res_path) as f:  # считываем итоговый маршрут
            data = f.read()
            tour = [int(x) for x in data.split()[1:]]

        self.rotate_to_start(tour, start=0)

        os.chdir(cur_dir)
        return [tour], output

    def parse_solution(self):
        """
        Парсим файл решения
        """
        solution = tsplib95.load_solution(self.res_path)
        return np.array(solution.tours[0])

    def dump_matrix(self):
        """
        Записываем матрицу, которую будет использовать солвер
        """
        with open(PROBLEM_FILE, "w") as dest:
            dest.write(dumps_matrix(self.problem.matrix))

    def rotate_to_start(self, route, start):
        """
        Прокручиваем маршрут, чтобы он начинался из начала
        """
        while route[0] != start:
            route = route[1:] + route[:1]
        return route


# TODO: Добавить солвер, который LKH, потом конкорд
# TODO: Написать методы кластеризации и сравнить их качество
