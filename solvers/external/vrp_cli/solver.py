"""В этом модуле находится интерфейс к растовскому солверу."""
from typing import Dict, List, Optional
import ujson
import os

import settings
from formats.pragmatic.matrices import build_matrices
from formats.pragmatic.problem import dumps_problem
from formats.pragmatic.solution import load_solution
from models.rich_vrp.problem import RichVRPProblem
from models.rich_vrp.solution import VRPSolution
from solvers.base import BaseSolver
from solvers.external.cmd import CommandRunner
from utils.logs import logger

problem_file = "problem.pragmatic"
solution_file = "solution.pragmatic"
geojson_file = "solution.geojson"

files_folder = "rust_solver"


class RustSolver(BaseSolver):
    """Интерфейс для солвера vrp-cli."""

    def __init__(
        self,
        initial_solution_file: Optional[str] = None,
        max_time: int = 300,
        max_generations: int = 3000,
        variation_generations: int = 200,
        min_variation: int = 0.1,
        show_log: bool = True,
        return_geojson=False,
    ):
        # Названия входных и выходных файлов
        self.initial_solution_file: Optional[
            str
        ] = initial_solution_file  # TODO: принимать само решение

        # Параметры солвера
        self.max_time: int = max_time
        self.max_generations: int = max_generations
        self.variation_generations: int = variation_generations
        self.min_variation: float = min_variation
        self.show_log: bool = show_log
        self.return_geojson: bool = return_geojson

        # Параметры рантайма
        self.matrix_files: Optional[
            Dict[str, str]
        ] = None  # Список файлов матриц расстояний.
        self.problem: Optional[RichVRPProblem] = None  # Решаемая задача
        self.solution: Optional[VRPSolution] = None  # Полученное решение

        self.problem_data: Optional[str] = None  # То, что записано в файле проблемы
        self.initial_solution_data: Optional[
            str
        ] = None  # Текстовое представление начального решения
        self.matrices: Optional[
            Dict[str, str]
        ] = None  # Матрицы расстояний для каждого профиля

        self.logs: Optional[List[str]] = None
        self.solution_data: Optional[str] = None
        self.solution_geojson: Optional[str] = None

    def command(self, path) -> str:
        """Получаем команду, которой будет запускаться растовский солвера.
        s
                Returns
                -------
                Строковое представление команды для запуска солвера
        """
        params = [
            f"{settings.VRP_CLI_PATH} solve",  # вызываем решалку
            f"pragmatic {path / problem_file}",  # файл, в котором сфорумлирована проблема
            f'{" ".join(["-m " + str(path / str(i)) for i in self.matrix_files])}',  # матрицы расстояний
            f"-o {path / solution_file}",  # куда писать результат
        ]
        params += [f"--geo-json={path / geojson_file}"] * bool(
            self.return_geojson
        )  # вывод geojson
        params += [f"--log"] * bool(self.show_log)  # показывать лог на экране
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

        # возможность передавать начальное решение
        params += [f"-i {self.initial_solution_file}"] * bool(
            self.initial_solution_file
        )

        return " ".join(params)

    def build_data(self):
        """Собираем все файлы для решения проблемы."""

        self.matrix_files = {
            f"matrix_{profile}.json": matrix
            for profile, matrix in build_matrices(self.problem.matrix).items()
        }

        self.problem_data = dumps_problem(self.problem)

    def assemble_solution(self) -> VRPSolution:
        """Собираем VRPSolution из результатов работа."""
        raise NotImplementedError

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

        self.problem = problem  # сохраняем проблему
        self.build_data()  # получаем все данные для солвера из проблемы

        logger.info('Строим входные файлы vrp-cli...')
        input_files = {problem_file: self.problem_data}
        if self.initial_solution_file:
            input_files[self.initial_solution_file] = (self.initial_solution_data,)

        # Получаем список выходных файлов
        output_files = [solution_file] + [geojson_file] * bool(self.return_geojson)
        problem_dir = settings.TMP_DIR / "rust_solver" / str(problem.name)
        os.makedirs(problem_dir, exist_ok=True)

        for matrix in self.matrix_files:
            with open((problem_dir / matrix), "w") as f:
                f.write(self.matrix_files[matrix])

        logger.info('Запускаем солвер...')
        runner = CommandRunner(
            command=self.command(problem_dir),
            input_files=input_files,
            output_files=output_files,
            files_dir=problem_dir,
            base_dir=problem_dir,
        ).run()
        print("AAA" * 20)
        # Получаем результат
        self.solution_data = runner.output_files_data[str(problem_dir / solution_file)]
        if self.return_geojson:
            self.solution_geojson = runner.output_files_data[geojson_file]

        return load_solution(problem, self.solution_data)
