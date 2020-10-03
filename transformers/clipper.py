import numpy as np

from data_structures.tour.array_tour import get_inf
from models.problems.base import BaseRoutingProblem
from models.rich_vrp.solution import VRPSolution
from transformers.base import BaseTransformer


def clip_matrix(
        a: np.ndarray,
        a_min: float = None,
        a_max: float = None,
) -> None:
    """
    Убираем значения меньше и больше пределов
    :param a: матрица
    :param a_min: минимальное расстояние
    :param a_max: максимальное расстояние
    :return:
    """
    np.clip(a, a_min, a_max, out=a)


def remove_longer(
        a: np.ndarray,
        a_max: float = None,
        inf: float = None,
) -> None:
    """
    Заменяем все числа больше a_max на бесконечность
    :param a:
    :param a_max:
    :param inf:
    :return:
    """
    if inf is None:
        inf = get_inf(a)

    a[a > a_max] += inf  # += чтобы даже если inf, то была разница


def make_symmetric(m: np.ndarray) -> None:
    """
    Делает матрицу симметричой методом усреднения
    """
    m += m.T
    m /= 2


class DistanceClipper(BaseTransformer):
    """
    Оставляем в матрице только ребра от a_min до a_max.
    Меньшие ребра клипаются, а большие заменяются на бесконечность

    save_matrix определет хотим ли мы сохранить матрицу, чтобы потом восстановить
    # TODO: сохранять только изменяемые куски
    """

    def __init__(
            self,
            a_min: float = None,
            a_max: float = None,
            inf: float = None,
            save_matrix: bool = True,
    ):
        self.a_min = a_min
        self.a_max = a_max
        self.inf = inf
        self.save_matrix = save_matrix
        self.matrix = None

    def transform(self, problem: BaseRoutingProblem) -> BaseRoutingProblem:
        if self.save_matrix:
            self.matrix = problem.matrix

        clip_matrix(problem.matrix, a_min=self.a_min)
        remove_longer(problem.matrix, a_max=self.a_max, inf=self.inf)

        return problem

    def restore(self, solution: VRPSolution) -> VRPSolution:
        if self.save_matrix:
            solution.problem.matrix = self.matrix

        return solution
