"""В этом модуле находится интерфейс к растовскому солверу."""
import os
import uuid
from pathlib import Path
from typing import Dict, Optional, List, Tuple

import ujson

from madrich import settings
from madrich.models.rich_vrp.plan import Plan
from madrich.models.rich_vrp.problem import RichVRPProblem, RichMDVRPProblem
from madrich.models.rich_vrp.solution import VRPSolution, MDVRPSolution
from madrich.solvers.base import BaseSolver
from madrich.solvers.vrp_cli.dump import dump_matrices, dump_problem
from madrich.solvers.vrp_cli.load_solution import load_solution
from madrich.utils.logs import logger


class RustSolver(BaseSolver):
    """Интерфейс для солвера vrp-cli."""

    def __init__(
        self,
        show_log: bool = True,
        default_params: bool = True,
        max_time: int = 300,
        max_generations: int = 3000,
        variation_generations: int = 200,
        min_variation: int = 0.1,
    ):
        # Параметры солвера
        self.default_params: bool = default_params
        self.max_time: int = max_time
        self.max_generations: int = max_generations
        self.variation_generations: int = variation_generations
        self.min_variation: float = min_variation
        self.show_log: bool = show_log

        # Параметры рантайма
        self.matrix_files: Optional[
            Dict[str, str]
        ] = None  # Список файлов матриц расстояний.
        self.solution: Optional[VRPSolution] = None  # Полученное решение

        self.problem_data: Optional[str] = None  # То, что записано в файле проблемы
        self.matrices: Optional[
            Dict[str, str]
        ] = None  # Матрицы расстояний для каждого профиля

        self.solution_data: Optional[str] = None

    def command(self, path: Path, problem_file: str, solution_file: str) -> str:
        """Получаем команду, которой будет запускаться растовский солвера.
        Returns
        -------
        Строковое представление команды для запуска солвера
        """
        params = [
            f"{settings.VRP_CLI_PATH} solve",  # вызываем решалку
            f"pragmatic {path / problem_file}",  # файл, в котором сформулирована проблема
            f'{" ".join(["-m " + str(path / str(i)) for i in self.matrix_files])}',  # матрицы расстояний
            f"-o {path / solution_file}",  # куда писать результат
        ]
        params += [f"--log"] * bool(self.show_log)  # показывать лог на экране

        if not self.default_params:
            params += [f"--max-time={self.max_time}"] * bool(
                self.max_time
            )  # максимальное время работы
            params += [f"--max-generations={self.max_generations}"] * bool(
                self.max_generations  # максимальное количетсво поколений оптимизации
            )
            # насколько медленно нужно оптимизировать, чтобы перестать
            params += (
                [f"--cost-variation={self.variation_generations},{self.min_variation}"]
                * bool(self.variation_generations)
                * bool(self.min_variation)
            )

        return " ".join(params)

    def solve(self, problem: RichVRPProblem) -> VRPSolution:
        """
        Решаем проблему и получаем решение
        Parameters
        ----------
        problem : Задача для солвера

        Returns
        -------
        Решение проблемы
        """
        logger.info(f"Решаем vrp_cli {problem.info()} ...")

        logger.info('Строим входные файлы vrp-cli...')
        problem_id = str(uuid.uuid4())

        problem_dir = settings.TMP_DIR / "rust_solver" / problem_id
        os.makedirs(problem_dir, exist_ok=True)
        problem_file = problem_dir / 'problem.json'
        solution_file = problem_dir / 'solution.json'

        dump_problem(problem_file, problem_dir, problem)
        self.matrix_files = dump_matrices(problem_dir, problem)

        logger.info('Запускаем солвер...')
        os.system(self.command(problem_dir, problem_file, solution_file))
        logger.info('Решение получено')

        logger.info('Получаем результат')
        with open(solution_file, 'r') as f:
            solution = ujson.load(f)
        return load_solution(problem, solution)

    def solve_mdvrp(self, problem: RichMDVRPProblem) -> MDVRPSolution:
        """
        Решаем проблему, состояющую из некскольких, и получаем несколько решений
        Parameters
        ----------
        problem : Задача для солвера

        Returns
        -------
        Решение проблемы
        """
        solutions = MDVRPSolution(problem)

        for sub_problem in problem.sub_problems:  # по сути решаем проблему для каждого депо
            solution = self.solve(sub_problem)  # запускаем наконец солвер
            solutions.merge(solution)
            self._cut_windows(solutions, problem)

        return solutions

    @staticmethod
    def _cut_windows(solutions: MDVRPSolution, problem: RichMDVRPProblem) -> None:
        """
        Нам нужно поменять окна с учетом нового решения после запуска солвера - время курьеров уже занято
        Нужно учесть, что они ездят между складами - на это тоже уходит время
        """
        for agent in problem.agents:
            new_tw = []
            for time_window in agent.time_windows:
                new_tw += RustSolver._cut_window(time_window, solutions.routes[agent.id])

    @staticmethod
    def _cut_window(time_window: Tuple[int, int], plans: List[Plan]) -> List[Tuple[int, int]]:
        """
        Режем конкретное окно с учетом маршрутов
        """


