"""
Базовый интерфейс для штуки, которая что-то решает
TODO: как удобнее, передавать проблему в конструктор или в метод solve?
 по идее в конструктор можно передавать параметры инициализации солвера

TODO: слишком большая иерархия базовый классов-солверов мешает адекватному дебагу
"""
from abc import abstractmethod

from models.problems.base import BaseRoutingProblem
from models.rich_vrp.solution import VRPSolution


class BaseSolver:
    """
    Абстрактная штука, которая умеет что-то решать
    TODO: а если параметры солвера зависят от проблемы? (Пример — LKH)
    """

    @abstractmethod
    def solve(self, problem: BaseRoutingProblem) -> VRPSolution:
        raise NotImplementedError


class SolverWrapper(BaseSolver):
    """
    Штука, которая решает что-то при помощи поля real_solver и делает вид, что это она сама решила.
    """
    def __init__(self, real_solver: BaseSolver):
        self.real_solver: BaseSolver = real_solver

    def solve(self, p: BaseRoutingProblem) -> VRPSolution:
        return self.real_solver.solve(p)
