from dataclasses import dataclass
from itertools import product

import numpy as np

from models.problems.base import BaseRoutingProblem

import matplotlib.pyplot as plt

from models.solutions.base import Tour


@dataclass
class Point2D:
    x: float
    y: float


class EuclidTSPProblem(BaseRoutingProblem):
    def __init__(self, points: np.ndarray):
        """
        :param points: массив расстояний
        """
        self.points = points

    def build_matrix(self, points) -> None:
        """
        Считаем матрицу расстояний
        """
        n = len(points)
        self.matrix = np.empty((n, n))
        for i, j in product(range(n), repeat=2):
            self.matrix[i, j] = np.linalg.norm(points[i] - points[j])  # noqa тупые стабы

    def lkh_par(self):
        pass

    def pragmatic(self):
        pass


class EuclidTSPTour(Tour):
    def __init__(self, problem: BaseRoutingProblem, nodes: np.ndarray):
        super().__init__(problem, nodes)
        ...

    # TODO: эти функции вообще не отсюда, их в MTSP нужно сдать
    def plot_tour(self, points, col="b"):
        """
        Рисуем один лепесток
        """
        plt.scatter(points[:, 0], points[:, 1], s=2, c="r")
        c = list(points) + [points[0]]
        plt.plot(*zip(*c), c=col, linewidth=0.5)

    def plot_tours(self, routes, points, col=None):
        """ Рисуем несколько лепестков """
        for r in routes:
            # print(list(r), calc_len(points[r]))
            # TODO: принтить длину каждого тура
            self.plot_tour(points[r], col=col)

