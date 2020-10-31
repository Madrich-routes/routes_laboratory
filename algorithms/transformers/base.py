"""
Базовый класс для всех трансформеров.
TODO: заменить cprint на rich
TODO: очень похоже на mw, поменять
"""
from copy import deepcopy

import numpy as np
from termcolor import cprint

from models.problems.base import BaseRoutingProblem
from models.solutions.base import VRPSolution


class BaseTransformer:
    """
    Этот класс описывает сведение одной задачи к другой. (Пример: ATSP сводится к TSP)
    1. Метод transform преобразует эту задачу к оригинальной
    2. Метод restore преобразует оригинальную задачу

    TODO: а что если потребуется передать параметры в трансформер, когда проблема станет известна?
    """

    def transform(self, problem: BaseRoutingProblem) -> BaseRoutingProblem:
        raise NotImplementedError

    def restore(self, solution: VRPSolution) -> VRPSolution:
        raise NotImplementedError

    def print_transform(self, p: BaseRoutingProblem, heading_color="on_green"):
        cprint("Initial:", on_color=heading_color)
        print(p)

        self.transform(p)

        cprint("Transformed:", on_color=heading_color)
        print(p)

        self.restore(p)

        cprint("Transformed back:", on_color=heading_color)
        print(p)

    def back_and_forth(self, p: BaseRoutingProblem):
        # self.transform(p)
        # self.restore(p)
        # TODO: это вообще нужно?
        ...

    def _save_old_data(self, p: BaseRoutingProblem):
        """
        Сохраняет данные оригинальной проблемы, чтобы потом иметь возможность восстановить их
        TODO: должен быть реализован в этом классе
        """
        ...
        # raise NotImplementedError

    def _restore_old_data(self, p: BaseRoutingProblem):
        """
        Восстанавливает данные оригинальной проболемы
        TODO: должен быть реализован в этом классе
        """


def wrap_function(instantiated_transformer: BaseTransformer):
    """
    Функция, которая позволяет принять на вход уже сконструированный трансформер
    И отдать его, как будто его все еще нужно инстанцировать
    """
    def wrapper():
        return instantiated_transformer

    return wrapper
