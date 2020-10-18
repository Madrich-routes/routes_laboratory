from typing import List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import numba as nb

array = np.ndarray
vector = nb.typed.List


def print_matrix(matrix: array):
    """ Вывод матрицы """
    string = ''
    for s in matrix:
        for elem in s:
            string += f'{elem}\t'
        string += '\n'
    print(string)


@nb.njit
def to_list(points: array) -> List[Tuple[float, float]]:
    """ array n * 2 to List[Point], Point = float, float
    :param points: points in ndarray format
    :return: points in list format
    """
    temp = []
    for point in points:
        temp.append((point[0], point[1]))
    return temp


def to_array(points: List[Tuple[float, float]]) -> array:
    """ List[Point] to array, Point = float, float
    :param points: points in list format
    :return: points in ndarray format
    """
    return np.array(points, dtype=('f8', 'f8'))


def draw_route(tour, nodes, color='r', show=True) -> None:
    first, second = tour[-1], tour[0]
    [y1, x1] = nodes[first]
    [y2, x2] = nodes[second]
    plt.plot([x1, x2], [y1, y2], linewidth=1, color=color)
    for idx in range(len(tour) - 1):
        [y1, x1] = nodes[tour[idx]]
        [y2, x2] = nodes[tour[idx + 1]]
        plt.plot([x1, x2], [y1, y2], linewidth=1, color=color)
    if show:
        plt.show()


def draw_points(nodes, color='r', show=False) -> None:
    tour = [i for i in range(len(nodes))]
    for idx in range(len(tour) - 1):
        [y1, x1] = nodes[tour[idx]]
        [y2, x2] = nodes[tour[idx + 1]]
        plt.plot([x1, x2], [y1, y2], f'{color}o', linewidth=1)
    if show:
        plt.show()


def draw_tours(tours: vector, nodes) -> None:
    colors = ['b', 'g', 'c', 'r', 'm', 'y', 'k']
    for segment in tours:
        idx = segment[0][0]
        for tour in segment:
            size = len(tour)
            for idy in range(size):
                first, second = tour[idy], tour[(idy + 1) % size]
                [y1, x1], [y2, x2] = nodes[first], nodes[second]
                plt.plot([x1, x2], [y1, y2], linewidth=1, color=colors[idx % len(colors)])
    plt.show()
