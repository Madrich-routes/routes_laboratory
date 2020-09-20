"""
В этом файле объявлены всякие штуки для объединения солверов и трансформеров.
TODO: Сейчас это очень похоже на MW, переделать
TODO: Перепроектировать, в таком виде это очень сложно дебагать.
 Совершенно не понятно откуда и куда ты попадаешь дебагером.
 Рандомно прыгаешь из одного трансформера в другой
"""

from abc import abstractmethod, ABC
from typing import List

from models.problems.base import BaseRoutingProblem
from solvers.base import BaseSolver
from transformers.base import BaseTransformer


class CompositeTransformer(BaseTransformer):
    """
    Трансформер, которй позыоляет объединить несколько трансформеров.
    Удобно, но иногда не очень удобно дебагать потом.
    """

    def __init__(self, transformers):
        super().__init__()

        self.debug = True
        self.transformers = transformers

    def transform(self, p: BaseRoutingProblem):
        for t in self.transformers:
            transformer_name = type(t)  # эта переменная здесь просто для того, чтобы видеть ее в дебагере
            if self.debug:
                print(f'Transform {transformer_name}')

            t.transform(p)

    def restore(self, p: BaseRoutingProblem):
        for t in reversed(self.transformers):
            if self.debug:
                print(f'Restore {type(t)}')

            t.restore(p)


class BaseTransformationalSolver(CompositeTransformer, BaseSolver, ABC):
    """
    1. Применяет все переданные трансформы и сводит задачу к простой форме.
    2. Решает задачу basic_solve
    3. Восстанавливает решение оригинальной задачи из упрощенной задачи

    Наследник должен реализовать функцию basic_solve
    """

    def solve(self, p: BaseRoutingProblem) -> BaseRoutingProblem:
        self.transform(p)
        try:
            self.basic_solve(p)
        finally:
            self.restore(p)

        return p

    @abstractmethod
    def basic_solve(self, p: BaseRoutingProblem):
        raise NotImplementedError


class TransformationalSolver(BaseTransformationalSolver):
    """
    1. Применяет все переданные трансформы и сводит задачу к простой форме.
    2. Решает задачу переданным солвером
    3. Восстанавливает решение оригинальной задачи из упрощенной задачи
    """

    def __init__(self, transformers: List, basic_solver: BaseSolver):
        super().__init__(transformers)
        self.basic_solver = basic_solver

    def basic_solve(self, p: BaseRoutingProblem):
        self.basic_solver.solve(p)
