import numpy as np
import tsplib95

from madrich import settings
from madrich.models.problems.base import LKHSolvable, BaseRoutingProblem
from madrich.solvers.external.interface import exec_and_log
from madrich.solvers.transformational import BaseTransformationalSolver


class LKHSolver(BaseTransformationalSolver):
    def __init__(
        self,
        tsp_path: str = settings.PROBLEM_FILE,
        par_path: str = settings.LKH_PAR_FILE,
        res_path: str = settings.VRP_RES_FILE,
        solver_path: str = settings.LKH3_PATH,
        trace_level: int = 2,  # 1-3

        runs: int = None,
        max_trials: int = None,  # дефолтные значения нужно перепроверить
        special: bool = False,

        initial_tour: str = 'WALK',
    ):
        """
        Trace level может быть от 1 до 3
        MAX_CANDIDATES = 4
        MAX_SWAPS = 400
        MAX_TRIALS = 1000
        KICKS = 0
        RUNS = 2
        TODO: PRECISION
        TODO: jinja
        """
        super().__init__(
            transformers=[
                # MatrixScaler(max_value=262144)
            ]
        )
        self.problem: LKHSolvable = None

        # TODO: к этим парням нужно приделать uuid,
        self.tsp_path: str = tsp_path
        self.par_path: str = par_path
        self.res_path: str = res_path

        self.solver_path: str = solver_path
        self.trace_level: int = trace_level

        # -------------------------------------- ПАРАМЕТРЫ LKH ---------------------------------------------------
        self.special = special
        self.runs = runs
        self.max_trials = max_trials
        self.initial_tour = initial_tour

    def basic_solve(self, p: BaseRoutingProblem):
        print("Начинаем формулировать файлы...")
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
        output = exec_and_log([self.solver_path, self.par_path])
        # output = subprocess.check_output([self.solver_path, self.par_path], shell=False)
        return self.parse_solution(), output

    def parse_solution(self):
        """Парсим файл решения."""
        solution = tsplib95.load_solution(self.res_path)
        return np.array(solution.tours[0])

    def solver_par(self) -> str:
        """Часть файла параметров, которая относится к конфигурации солвера."""
        return '\n'.join([
            f"PROBLEM_FILE = {self.tsp_path}",
            f"TOUR_FILE = {self.res_path}",

            f"SINTEF_SOLUTION_FILE = /tmp/lkh.sintef",
            f"CANDIDATE_FILE= /tmp/lkh.cand",
            f"PI_FILE = /tmp/lkh.pi",
            f"MTSP_SOLUTION_FILE = /tmp/lkh.pi",

            f"TRACE_LEVEL = {self.trace_level}",
            f'PRECISION = 1',

            f'RECOMBINATION = GPX2',
            f'POPULATION_SIZE = 10',

            f'INITIAL_TOUR_ALGORITHM = {self.initial_tour}',

            f'SUBGRADIENT = NO',
            f'CANDIDATE_SET_TYPE = POPMUSIC',
            f'POPMUSIC_INITIAL_TOUR = YES',
            f'POPMUSIC_MAX_NEIGHBORS = 10',
            f'POPMUSIC_SAMPLE_SIZE = 20',
            f'POPMUSIC_SOLUTIONS = 30',
            f'POPMUSIC_TRIALS = 1',

            f'MAKESPAN = YES',
            r'# ' * (not self.special) + 'SPECIAL',

            f'MAX_TRIALS = {self.max_trials}',
            f'RUNS = {self.runs}',
        ])

    def dumps_params(self) -> str:
        """Итоговая строка параметров с учетом параметров проболемы."""
        return self.solver_par() + '\n' + self.problem.lkh_par()

    def dumps_problem(self) -> str:
        """Получаем строку с tsplib описание проблемы."""
        return self.problem.lkh_problem()

    def dump_problem(self) -> None:
        with open(self.par_path, "w") as dest:
            dest.write(self.dumps_params())

        with open(self.tsp_path, "w") as dest:
            dest.write(self.dumps_problem())