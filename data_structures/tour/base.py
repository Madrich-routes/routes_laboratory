import numpy as np

from models.problems.base import BaseRoutingProblem


class Tour:
    """
    Круговой маршрут без повторов.
    Начинается и заканчивается в одной и той же точке.
    """

    def __init__(
            self,
            problem: BaseRoutingProblem,
            nodes: np.ndarray
    ):
        """
        TODO: тут, возможно, нужно хранить того кто именно объезжает этот тур
        :param problem:
        :param nodes:
        """
        self.problem = problem
        self.nodes = nodes

    @property
    def size(self):
        """
        Считаем длину маршрута в количестве точек
        """
        return len(self.nodes)

    def distance(self):
        """
        Общая длина тура
        """
        raise NotImplementedError

    def prev(self, a: int):
        raise NotImplementedError

    def next(self, a: int):
        raise NotImplementedError

    def between(self, a: int, b: int, c: int) -> bool:
        raise NotImplementedError

    def flip(self, a: int, b: int, c: int, d: int) -> None:
        raise NotImplementedError

    def edges(self):
        raise NotImplementedError
