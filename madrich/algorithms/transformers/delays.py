"""Это модуль с очень простым преобразованием.

Он прибавляет время пребывания в точке к матрице временн перемещений таким образом, чтобы получить
эквивалентную задачу без задержек
"""
import numpy as np
from transformers.base import BaseTransformer

from madrich.models.problems import BaseRoutingProblem, WithDelays
from madrich.models.rich_vrp.solution import VRPSolution


def remove_delays(matrix: np.ndarray, delays: np.ndarray, restore=False) -> None:
    """Убираем задержки. Матрица меняется на месте.

    :param restore: восстанавливаеи или удаляем
    :param matrix: matrix[i][j] — время перемещения i->j
    :param delays: delays[i] — сколько времени нужно провести в этой точке
    """
    if not restore:
        matrix += delays[:, np.newaxis]
    else:
        matrix -= delays[:, np.newaxis]


class DelaysRemover(BaseTransformer):
    def __init__(self):
        self.delays = None

    def transform(self, problem: WithDelays) -> BaseRoutingProblem:
        remove_delays(matrix=problem.matrix, delays=problem.delays)
        return problem

    def restore(self, solution: VRPSolution) -> VRPSolution:
        solution.problem.matrix = solution.problem
        return solution
