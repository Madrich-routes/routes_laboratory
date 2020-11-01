from typing import List, Optional, Dict

from models.rich_vrp.problem import RichVRPProblem
from models.rich_vrp.solution import VRPSolution
from solvers.base import BaseSolver
from solvers.external.cmd import CommandRunner
from utils.logs import logger

problem_file = 'problem.pragmatic'
solution_file = 'solution.pragmatic'
geojson_file = 'solution.geojson'

files_folder = 'rust_solver'


class RustSolver(BaseSolver):
    """
    Интерфейс для солвера vrp-cli
    """

    def __init__(
            self,
            problem_file: str = "./tmp/problem.pragmatic",
            solution_file: str = "./tmp/solution.pragmatic",
            geojson_file: Optional[str] = "./tmp/solution.geojson",
            initial_solution_file: Optional[str] = None,
            max_time: int = 300,
            max_generations: int = 3000,
            variation_generations: int = 200,
            min_variation: int = 0.1,
            show_log: bool = True,
    ):
        # Названия входных и выходных файлов
        self.problem_file: str = problem_file
        self.initial_solution_file: Optional[str] = initial_solution_file

        self.solution_file: str = solution_file
        self.geojson_file: Optional[str] = geojson_file

        # Параметры солвера
        self.max_time: int = max_time
        self.max_generations: int = max_generations
        self.variation_generations: int = variation_generations
        self.min_variation: float = min_variation
        self.show_log: bool = show_log

        # Параметры рантайма
        self.matrix_files: Optional[List[str]] = None  # Список файлов матриц расстояний. Генерируется из проблемы.
        self.problem: Optional[RichVRPProblem] = None  # Решаемая задача
        self.solution: Optional[VRPSolution] = None  # Полученное решение

        self.problem_data: Optional[str] = None  # То, что записано в файле проблемы
        self.initial_solution_data: Optional[str] = None  # Текстовое представление начального решения
        self.matrices: Optional[Dict[str, str]] = None  # Матрицы расстояний для каждого профиля

        self.logs: Optional[List[str]] = None
        self.solution_data: Optional[str] = None
        self.solution_geojson: Optional[str] = None

    def command(self) -> str:
        """
        Получаем команду, которой будет запускаться растовский солвера

        Returns
        -------
        Строковое представление команды для запуска солвера
        """
        params = [
            f"vrp-cli solve",  # вызываем решалку
            f"pragmatic {self.problem_file}",  # файл, в котором сфорумлирована проблемаы
            f'{" ".join(self.matrix_files)}',  # матрицы расстояний
            f"-o {self.solution_file}",  # куда писать результат
        ]
        params += [f"--geo-json={self.geojson_file}"] * bool(self.geojson_file)  # вывод geojson
        params += [f"--log"] * bool(self.show_log)  # показывать лог на экране
        params += [f"--max-time={self.max_time}"] * bool(self.max_time)  # максимальное время работы
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
        params += [f'-i {self.initial_solution_file}'] * bool(self.initial_solution_file)

        return " ".join(params)

    def build_data(self) -> None:
        """
        Собираем все файлы для решения проблемы
        """

    def assemble_solution(self) -> VRPSolution:
        """
        Собираем VRPSolution из результатов работа
        """

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
        logger.info(f'Решаем vrp_cli {problem.info()} ...')
        self.problem = problem
        self.build_data()

        # Получем входные файлы
        input_files = {self.problem_file: self.problem_data}
        if self.initial_solution_file:
            input_files[self.initial_solution_file] = self.initial_solution_data,

        # Получаем выходные файлы
        output_files = [self.solution_file]
        output_files += [self.geojson_file] * bool(self.geojson_file)

        runner = CommandRunner(
            command=self.command(),
            input_files=input_files,
            output_files=output_files,
            files_dir='rust_solver',
            base_dir='rust_solver',
        ).run()

        return self.assemble_solution()
