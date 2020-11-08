"""Базовый интерфейс для штуки, которая что-то решает.

TODO: слишком большая иерархия базовый классов-солверов мешает адекватному дебагу
"""
from abc import abstractmethod

from models.problems.base import BaseRoutingProblem
from models.rich_vrp.solution import VRPSolution


class BaseSolver:
    """Абстрактная штука, которая умеет что-то решать При желании, в конструктор солвера можно передавать
    проблему.

    Но это не всегда является необходимым.
    """

    @abstractmethod
    def solve(self, problem: BaseRoutingProblem) -> VRPSolution:
        raise NotImplementedError


class SolverWrapper(BaseSolver):
    """Штука, которая решает что-то при помощи поля real_solver и делает вид, что это она сама решила."""
    def __init__(self, real_solver: BaseSolver):
        self.real_solver: BaseSolver = real_solver

    def solve(self, p: BaseRoutingProblem) -> VRPSolution:
        return self.real_solver.solve(p)
