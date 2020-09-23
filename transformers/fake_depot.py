import numpy as np

from data_structures.tour.array_tour import get_inf
from models.rich_vrp.problem import RichVRPProblem
from models.solutions.base import VRPSolution
from transformers.base import BaseTransformer


def add_fake_depot(
        matrix: np.ndarray,
        start_ids: np.ndarray,
        end_ids: np.ndarray,
) -> np.ndarray:
    """
    Эта функция работает только для тех задач, у которых машина просто едет из одной точки в другую

    :param matrix: матрица расстояний
    :param start_ids: id точек, в которык нужно начать
    :param end_ids: id точек, в которых нужно закончить
    :return: Новая матрица с добавленым депо в точке 0
    """
    n = len(matrix)
    res = np.zeros((n + 1, n + 1))
    res[1:, 1:] = matrix

    inf = get_inf(matrix)  # настолько большое ребро, что точно не попадет в тур

    res[0, :] = inf   # депо не связано с точками кроме начала и конца
    res[:, 0] = inf
    res[0, start_ids] = 0  # бесплатный проезд из начала в депо и наоборот
    res[end_ids, 0] = 0

    return res


class FakeDepot(BaseTransformer):
    """
    Добавляем фейковое депо с нулевыми стоимостями до начала и от конца
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

    def transform(self, problem: RichVRPProblem) -> RichVRPProblem:
        if self.save_matrix:
            self.matrix = problem.matrix

        problem.matrix = add_fake_depot(
            problem.matrix.dist,
            np.array(a.start_place for a in problem.agents),
            np.array(a.end_place for a in problem.agents),
        )

        return problem

    def restore(self, solution: VRPSolution) -> VRPSolution:
        if self.save_matrix:
            solution.problem.matrix = self.matrix

        return solution
